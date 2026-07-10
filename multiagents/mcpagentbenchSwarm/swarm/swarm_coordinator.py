"""
MCPAgentBench Swarm Coordinator — Role-Based Collaborative Decision Making.
Three role-agents collaborate on tool-calling decisions, then a ReAct
executor carries out the agreed plan:
1. ANALYST: Understands the user request, identifies what needs to happen
2. TOOL PLANNER: Selects specific tools and arguments from available tools
3. CRITIC: Validates the plan, checks for issues, agrees or requests changes
After consensus, a ReAct executor agent executes the tools with real bindings.
This tests whether collaborative decision-making (multiple perspectives)
improves tool selection vs single-agent reasoning (ReAct) or hierarchical
delegation (Orchestrator).
"""
import asyncio
from typing import Any, Dict, List, Optional
from langchain.agents import create_agent
from langchain_core.tools import BaseTool
from agenttim.agents.base import StatefulEvalAgent
from agenttim.agents.react_base import ReactEvalAgent
from agenttim.evaluation.eval_utils.multi_agent_metrics import AgentMessage
from agenttim.config.settings import Settings
from agenttim.mcpservers.mcpagentbench.domain_config import (

    ALL_DOMAINS,

    DOMAIN_DESCRIPTIONS,

    BASE_PROMPT,

    get_tool_to_domain_map,
)
from agenttim.multiagents.mcpagentbenchOrchestrator.mcpclients import BenchMCPClient
ANALYST_PROMPT = BASE_PROMPT + """
## Your Role: Request Analyst
Your job is to understand WHAT the user needs.
- Break down the user's request into concrete steps
- Identify which domains/categories are involved (e.g., dining, travel, finance)
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
class MCPBenchSwarmAgent(StatefulEvalAgent):

    """Role-based Swarm for MCPAgentBench.

    Three role-agents (Analyst, Planner, Critic) collaborate on decisions.
    A ReAct executor carries out the validated plan.
    """

    TURN_TIMEOUT = 180

    def __init__(

        self,

        settings: Settings,

        logger: Optional[Any] = None,

    ):

        super().__init__(settings, logger_name="MCPBenchSwarm", logger=logger)

        self._domain_tools: Dict[str, List[BaseTool]] = {}

        self._all_tools: List[BaseTool] = []

        self._mcp_clients: Dict[str, BenchMCPClient] = {}

        self._domain_tool_map: Dict[str, str] = {}

    async def _do_initialize(self) -> None:

        """Load all domain MCP tools."""

        self.logger.info("Initializing MCPBench Swarm Agent (role-based)")

        self._domain_tool_map = get_tool_to_domain_map()

        for domain in ALL_DOMAINS:

            client = BenchMCPClient(self.settings, domain)

            tools = await client.get_tools()

            self._mcp_clients[domain] = client

            self._domain_tools[domain] = tools

            self.logger.info(f"Loaded {len(tools)} tools for {domain}")

        self._all_tools = [t for tools in self._domain_tools.values() for t in tools]

        self.logger.info(f"Swarm Agent initialized ({len(self._all_tools)} total tools)")

    def setup_for_test_case(

        self,

        tools: list | None = None,

        **kwargs: Any,

    ) -> None:

        """Set tools for this test case."""

        super().setup_for_test_case()

        if tools is not None:

            self._all_tools = list(tools)

    async def _run_analyst(

        self, user_request: str, callbacks: list | None = None,

    ) -> str:

        """Analyst: understand the request."""

        prompt = ANALYST_PROMPT.format(user_request=user_request)

        llm_config = {"metadata": {"agent_name": "swarm_analyst"}}

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

        """Planner: select tools and arguments."""

        tool_defs = "\n".join(

            f"- {t.name}: {t.description}" for t in self._all_tools

        )

        prompt = PLANNER_PROMPT.format(

            tool_definitions=tool_defs,

            analyst_output=analyst_output,

        )

        llm_config = {"metadata": {"agent_name": "swarm_planner"}}

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

        """Critic: validate the plan."""

        tool_names = ", ".join(t.name for t in self._all_tools)

        prompt = CRITIC_PROMPT.format(

            user_request=user_request,

            analyst_output=analyst_output,

            planner_output=planner_output,

            tool_names=tool_names,

        )

        llm_config = {"metadata": {"agent_name": "swarm_critic"}}

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

        """Execute the validated plan via ReAct agent."""

        executor_prompt = EXECUTOR_PROMPT.format(validated_plan=validated_plan)

        safe_tools = [ReactEvalAgent._wrap_tool_safe(t) for t in self._all_tools]

        llm_config: dict[str, Any] = {"metadata": {"agent_name": "swarm_executor"}}

        if callbacks:

            llm_config["callbacks"] = callbacks

        llm = self._llm.with_config(llm_config)

        executor = create_agent(

            llm,

            tools=safe_tools,

            system_prompt=executor_prompt,

        )

        executor = executor.with_config({"recursion_limit": 20})

        invoke_config: dict[str, Any] = {"metadata": {"agent_name": "swarm_executor"}}

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

        """Three-phase turn: Analyst → Planner → Critic → Executor."""

        messages: list[AgentMessage] = []

        t = 0.0

        if verbose:

            print("  [1/4] Analyst analyzing request...")

        analyst_output = await self._run_analyst(user_message, callbacks)

        messages.append(AgentMessage(

            sender="analyst", recipient="planner",

            content=analyst_output[:500],

            message_type="analysis",

            timestamp=t, token_count=len(analyst_output.split()),

        ))

        t += 1.0

        if verbose:

            print(f"    Analyst: {analyst_output[:150]}...")

        if verbose:

            print("  [2/4] Planner selecting tools...")

        planner_output = await self._run_planner(

            user_message, analyst_output, callbacks,

        )

        messages.append(AgentMessage(

            sender="planner", recipient="critic",

            content=planner_output[:500],

            message_type="plan",

            timestamp=t, token_count=len(planner_output.split()),

        ))

        t += 1.0

        if verbose:

            print(f"    Planner: {planner_output[:150]}...")

        if verbose:

            print("  [3/4] Critic validating plan...")

        critic_output = await self._run_critic(

            user_message, analyst_output, planner_output, callbacks,

        )

        messages.append(AgentMessage(

            sender="critic", recipient="executor",

            content=critic_output[:500],

            message_type="validation",

            timestamp=t, token_count=len(critic_output.split()),

        ))

        t += 1.0

        if verbose:

            print(f"    Critic: {critic_output[:150]}...")

        validated_plan = (

            f"Request Analysis:\n{analyst_output}\n\n"

            f"Tool Plan:\n{planner_output}\n\n"

            f"Validation:\n{critic_output}"

        )

        if callbacks:

            for cb in callbacks:

                if hasattr(cb, "messages"):

                    cb.messages.extend(messages)

                if hasattr(cb, "_delegation_count"):

                    cb._delegation_count = 1

        if verbose:

            print("  [4/4] Executor running tools...")

        response = await self._execute_plan(

            user_message, validated_plan, callbacks, verbose,

        )

        if verbose:

            print(f"    Result: {response[:150]}...")

        return response, None

    def get_available_subagents(self) -> Dict[str, str]:

        return {

            "analyst": "Analyzes user request and identifies requirements",

            "planner": "Selects tools and arguments from available pool",

            "critic": "Validates the execution plan for correctness",

            "executor": "Executes the validated plan via ReAct",

        }

    def get_tool_count(self) -> int:

        return len(self._all_tools)

