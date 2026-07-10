"""
BFCL Orchestrator Agent.
Coordinates 8 domain-specific subagents for BFCL multi-turn evaluation.
Each subagent is wrapped as a dedicated tool (per LangChain docs pattern).
"""
from typing import Any, Dict, List, Optional
from langchain_core.tools import tool
from agenttim.agents.react_base import ReactEvalAgent
from agenttim.config.settings import Settings
from agenttim.bfcl.domain_config import (

    BASE_PROMPT,

    DOMAIN_DESCRIPTIONS,

    DOMAIN_TOOLS,

    get_tool_to_domain_map,
)
from agenttim.multiagents.bfclOrchestrator.subagents.agent_definitions import (

    AGENT_REGISTRY,
)
SUPERVISOR_PROMPT = BASE_PROMPT + """
## Orchestrator Role
You are a coordinator. Your tools are specialized subagents — choose the right one(s) for the user's request.
- Include ALL relevant parameters from the user's request in the delegation
- For multi-domain requests, call multiple subagent tools in sequence
- For sequential tasks, pass results from one subagent to the next
## Subagent Context
Subagents receive the full conversation history including all previous tool calls and results.
They can see what happened in prior turns, so you don't need to repeat state information.
However, you should still resolve ambiguous references in your delegation:
- Convert "there", "that file", "the same one" into concrete values
- Be explicit about WHAT to do, the subagent knows the current state"""
class BFCLOrchestratorAgent(ReactEvalAgent):

    """Orchestrator for BFCL multi-turn evaluation.

    8 domain subagents, each exposed as a dedicated tool to the supervisor.
    """

    SYSTEM_PROMPT = SUPERVISOR_PROMPT

    RECURSION_LIMIT = 20

    def __init__(

        self,

        settings: Settings,

        granularity: str = "fine",

        logger: Optional[Any] = None,

    ):

        super().__init__(settings, logger_name="BFCLOrchestrator", logger=logger)

        self._subagents: Dict[str, Any] = {}

    async def _do_initialize(self) -> None:

        """Initialize all domain subagents and create supervisor agent."""

        for name, agent_class in AGENT_REGISTRY.items():

            agent = agent_class(settings=self.settings, logger=self.logger)

            await agent.initialize()

            self._subagents[name] = agent

            self.logger.info(f"Initialized subagent: {name}")

        supervisor_tools = self._make_subagent_tools()

        self._tools = supervisor_tools

        self._create_react_agent(supervisor_tools)

        self.logger.info(

            f"Orchestrator ready: {len(self._subagents)} subagents, "

            f"{len(supervisor_tools)} tools"

        )

    def setup_for_test_case(

        self,

        tools: Optional[List[Any]] = None,

        **kwargs: Any,

    ) -> None:

        """Redistribute sampled tools across subagents and rebuild supervisor."""

        super().setup_for_test_case()

        if tools is None:

            return

        tool_to_domain = get_tool_to_domain_map()

        grouped: dict[str, list] = {name: [] for name in self._subagents}

        for t in tools:

            domain = tool_to_domain.get(t.name)

            if domain and domain in grouped:

                grouped[domain].append(t)

        for name, subagent in self._subagents.items():

            subagent.set_tools(grouped.get(name, []))

        supervisor_tools = self._make_subagent_tools()

        self._tools = supervisor_tools

        self._create_react_agent(supervisor_tools)

        total = sum(len(v) for v in grouped.values())

        self.logger.info(

            f"Test case setup: {total} tools across {len(self._subagents)} subagents"

        )

    def _make_subagent_tools(self) -> list:

        """Create one tool wrapper per subagent.

        RunnableConfig is injected by LangGraph to propagate callbacks
        (TokenTracker, ToolTracker) to subagent LLM calls.

        History Propagation: The orchestrator's conversation history is passed
        to subagents via chat_with_history(). This allows subagents to see
        previous turns' tool calls and results, eliminating the need for
        redundant orientation calls (pwd, ls) in multi-turn scenarios.
        """

        from langchain_core.runnables import RunnableConfig

        tools = []

        for name, subagent in self._subagents.items():

            description = self._get_agent_description(name)

            logger = self.logger

            orchestrator = self

            async def fn(

                request: str, config: RunnableConfig,

                _agent=subagent, _name=name, _orchestrator=orchestrator,

            ) -> str:

                logger.info(f"Delegating to {_name}: {request[:100]}...")

                callbacks = config.get("callbacks", None)

                history = _orchestrator.get_conversation_history()

                try:

                    response = await _agent.chat_with_history(

                        request, history=history, callbacks=callbacks

                    )

                    logger.info(f"Subagent {_name} completed")

                    return response

                except Exception as e:

                    error_msg = f"Subagent {_name} failed: {e}"

                    logger.error(error_msg)

                    return error_msg

            fn.__name__ = f"{name}_agent"

            fn.__doc__ = description

            tools.append(tool(fn))

        return tools

    def _get_agent_description(self, name: str) -> str:

        desc = DOMAIN_DESCRIPTIONS.get(name, name)

        domain_tools = DOMAIN_TOOLS.get(name, [])

        tools_str = ", ".join(domain_tools[:10])

        suffix = f" +{len(domain_tools) - 10} more" if len(domain_tools) > 10 else ""

        return f"{desc}. Tools: {tools_str}{suffix}"

    def get_available_subagents(self) -> Dict[str, str]:

        return {

            domain: DOMAIN_DESCRIPTIONS.get(domain, "")

            for domain in self._subagents

        }

    async def get_state(self) -> Dict[str, Any]:

        """Read state from all MCP servers for evaluation comparison."""

        states: Dict[str, Any] = {}

        for name, subagent in self._subagents.items():

            mcp_client = subagent.get_mcp_client()

            if mcp_client:

                domain_state = await mcp_client.get_state()

                states.update(domain_state)

        return states

