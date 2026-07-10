"""
BFCL Swarm Coordinator — Role-Based Collaborative Decision Making.
Same architecture as MCPAgentBench Swarm: three role-agents collaborate
on tool-calling decisions, then a ReAct executor carries out the plan.
1. ANALYST: Understands the user request, identifies what needs to happen
2. TOOL PLANNER: Selects specific tools and arguments from available tools
3. CRITIC: Validates the plan, checks for issues, agrees or requests changes
After consensus, a ReAct executor agent executes the tools with real bindings.
"""
import asyncio
from typing import Any, Dict, List, Optional
from langchain_core.tools import BaseTool
from agenttim.agents.base import StatefulEvalAgent
from agenttim.agents.react_base import ReactEvalAgent
from agenttim.config.settings import Settings
from agenttim.bfcl.domain_config import (

    ALL_DOMAINS,

    BASE_PROMPT,

    DOMAIN_DESCRIPTIONS,

    get_tool_to_domain_map,
)
ANALYST_PROMPT = BASE_PROMPT + """
## Your Role: Request Analyst
Your job is to understand WHAT the user needs.
- Break down the user's request into concrete steps
- Identify which domains/categories are involved
- Determine if steps are independent (parallel) or dependent (sequential)
- Do NOT select specific tools — that's the Tool Planner's job
- Be concise and structured
## User Request
{user_request}
## Your Analysis:"""
PLANNER_PROMPT = BASE_PROMPT + """
## Your Role: Tool Planner
Your job is to select the RIGHT tools with the RIGHT arguments.
## Available Tools
{tool_definitions}
## Analyst's Assessment
{analyst_output}
## Instructions
- Select the specific tools needed to fulfill the request
- Specify exact argument values for each tool call
- If a tool depends on another's result, note the dependency
- Only use tools from the available list above
## Your Plan:"""
CRITIC_PROMPT = BASE_PROMPT + """
## Your Role: Plan Critic
Your job is to validate the tool execution plan.
## User Request
{user_request}
## Analyst's Assessment
{analyst_output}
## Tool Planner's Plan
{planner_output}
## Available Tools
{tool_names}
## Instructions
Check the plan for:
1. Are the selected tools correct for the request?
2. Are the arguments reasonable and complete?
3. Is the execution order correct (dependencies respected)?
4. Are there any missing steps?
If the plan looks good, say "APPROVED" and summarize the final plan.
If there are issues, explain what needs to change.
## Your Review:"""
EXECUTOR_PROMPT = BASE_PROMPT + """
## Your Role: Tool Executor
A team of experts has analyzed the user's request and created a validated plan. Execute it.
## Validated Plan
{validated_plan}
## Instructions
- Execute ALL tools in the plan with the specified arguments
- Follow the execution order (respect dependencies)
- Do NOT add tools that weren't in the plan
- Do NOT skip tools that were approved"""
class BFCLSwarmAgent(StatefulEvalAgent):

    """Role-based Swarm for BFCL multi-turn evaluation.

    Three role-agents (Analyst, Planner, Critic) collaborate on decisions.
    A ReAct executor carries out the validated plan.

    Same architecture as MCPBenchSwarmAgent — only the MCP client and
    domain config differ.
    """

    TURN_TIMEOUT = 120

    def __init__(

        self,

        settings: Settings,

        logger: Optional[Any] = None,

    ):

        super().__init__(settings, logger_name="BFCLSwarm", logger=logger)

        self._all_tools: List[BaseTool] = []

        self._tool_to_domain = get_tool_to_domain_map()

    async def _do_initialize(self) -> None:

        """LLM ready. Tools are distributed per test case."""

        self.logger.info("BFCL Swarm Agent initialized (role-based)")

    def setup_for_test_case(

        self,

        tools: Optional[List[Any]] = None,

        **kwargs: Any,

    ) -> None:

        """Set tools for this test case."""

        super().setup_for_test_case()

        if tools is not None:

            self._all_tools = list(tools)

    async def _run_analyst(

        self, user_request: str, callbacks: list | None = None,

    ) -> str:

        prompt = ANALYST_PROMPT.format(user_request=user_request)

        llm_config: dict[str, Any] = {"metadata": {"agent_name": "swarm_analyst"}}

        if callbacks:

            llm_config["callbacks"] = callbacks

        response = await self._llm.ainvoke([

            {"role": "system", "content": prompt},

        ], config=llm_config)

        return response.content

    async def _run_planner(

        self, user_request: str, analyst_output: str,

        callbacks: list | None = None,

    ) -> str:

        tool_defs = "\n".join(

            f"- {t.name}: {t.description}" for t in self._all_tools

        )

        prompt = PLANNER_PROMPT.format(

            tool_definitions=tool_defs,

            analyst_output=analyst_output,

        )

        llm_config: dict[str, Any] = {"metadata": {"agent_name": "swarm_planner"}}

        if callbacks:

            llm_config["callbacks"] = callbacks

        response = await self._llm.ainvoke([

            {"role": "system", "content": prompt},

        ], config=llm_config)

        return response.content

    async def _run_critic(

        self, user_request: str, analyst_output: str, planner_output: str,

        callbacks: list | None = None,

    ) -> str:

        tool_names = ", ".join(t.name for t in self._all_tools)

        prompt = CRITIC_PROMPT.format(

            user_request=user_request,

            analyst_output=analyst_output,

            planner_output=planner_output,

            tool_names=tool_names,

        )

        llm_config: dict[str, Any] = {"metadata": {"agent_name": "swarm_critic"}}

        if callbacks:

            llm_config["callbacks"] = callbacks

        response = await self._llm.ainvoke([

            {"role": "system", "content": prompt},

        ], config=llm_config)

        return response.content

    async def _execute_plan(

        self, user_request: str, validated_plan: str,

        callbacks: list | None = None, verbose: bool = False,

    ) -> str:

        """Create a ReAct executor and run the validated plan."""

        executor_prompt = EXECUTOR_PROMPT.format(validated_plan=validated_plan)

        safe_tools = [ReactEvalAgent._wrap_tool_safe(t) for t in self._all_tools]

        from langchain.agents import create_agent

        llm = self._llm.with_config({"metadata": {"agent_name": "swarm_executor"}})

        executor = create_agent(

            llm,

            tools=safe_tools,

            system_prompt=executor_prompt,

        )

        invoke_config: dict[str, Any] = {

            "recursion_limit": 20,

            "metadata": {"agent_name": "swarm_executor"},

        }

        if callbacks:

            invoke_config["callbacks"] = callbacks

        result = await asyncio.wait_for(

            executor.ainvoke(

                {"messages": [{"role": "user", "content": user_request}]},

                config=invoke_config,

            ),

            timeout=self.TURN_TIMEOUT,

        )

        return result["messages"][-1].text

    async def _execute_turn(

        self,

        user_message: str,

        callbacks: Optional[List[Any]] = None,

        verbose: bool = False,

    ) -> tuple[str, list | None]:

        """Run the 4-phase pipeline: Analyst → Planner → Critic → Executor."""

        if verbose:

            print("  [1/4] Analyst...")

        analyst_output = await self._run_analyst(user_message, callbacks)

        if verbose:

            print(f"    Analysis: {analyst_output[:150]}...")

        if verbose:

            print("  [2/4] Planner...")

        planner_output = await self._run_planner(

            user_message, analyst_output, callbacks,

        )

        if verbose:

            print(f"    Plan: {planner_output[:150]}...")

        if verbose:

            print("  [3/4] Critic...")

        critic_output = await self._run_critic(

            user_message, analyst_output, planner_output, callbacks,

        )

        if verbose:

            print(f"    Review: {critic_output[:150]}...")

        validated_plan = critic_output

        if verbose:

            print("  [4/4] Executor...")

        response = await self._execute_plan(

            user_message, validated_plan, callbacks, verbose,

        )

        if verbose:

            print(f"    Result: {response[:150]}...")

        return response, None

    def get_available_subagents(self) -> Dict[str, str]:

        return {

            "analyst": "Understands user request, identifies steps",

            "planner": "Selects tools and arguments",

            "critic": "Validates the execution plan",

            "executor": "Executes validated tool calls via ReAct",

        }

