"""
MCPAgentBench Orchestrator Agent.
Coordinates domain-specific subagents using the LangChain subagent pattern.
Each subagent is wrapped as a dedicated tool (per LangChain docs).
The supervisor sees one tool per domain with a clear description.
Supports two granularity modes:
- **fine**: 16 focused subagents, each with 1 MCP server
- **coarse**: 3 broad subagents, each with N MCP servers
"""
from typing import Any, Dict, List, Literal, Optional
from langchain_core.tools import tool
from agenttim.agents.react_base import ReactEvalAgent
from agenttim.config.settings import Settings
from agenttim.mcpservers.mcpagentbench.domain_config import (

    COARSE_AGENT_GROUPS,

    DOMAIN_DESCRIPTIONS,

    DOMAIN_TOOLS,

    BASE_PROMPT,

    get_tool_to_domain_map,
)
from agenttim.multiagents.mcpagentbenchOrchestrator.subagents.agent_definitions import (

    AGENT_REGISTRY,

    COARSE_AGENT_REGISTRY,
)
Granularity = Literal["fine", "coarse"]
SUPERVISOR_PROMPT = BASE_PROMPT + """
## Orchestrator Role
You are a coordinator. Your tools are specialized subagents — choose the right one(s) for the user's request.
- Include ALL relevant parameters from the user's request in the delegation
- For multi-domain requests, call multiple subagent tools in sequence
- For sequential tasks, pass results from one subagent to the next"""
class MCPBenchOrchestratorAgent(ReactEvalAgent):

    """
    Orchestrator that coordinates domain-specific subagents for MCPAgentBench.

    Each subagent is exposed as a dedicated tool to the supervisor.
    Supports fine (16 agents) and coarse (3 agents) granularity.
    """

    SYSTEM_PROMPT = SUPERVISOR_PROMPT

    RECURSION_LIMIT = 20

    def __init__(

        self,

        settings: Settings,

        granularity: Granularity = "fine",

        logger: Optional[Any] = None,

    ):

        super().__init__(settings, logger_name="MCPBenchOrchestrator", logger=logger)

        self.granularity = granularity

        self._agent = None

        self._subagents: Dict[str, Any] = {}

    async def _do_initialize(self) -> None:

        """Initialize subagents and create supervisor agent."""

        self.logger.info(

            f"Initializing MCPBench Orchestrator (granularity={self.granularity})"

        )

        registry = (

            COARSE_AGENT_REGISTRY

            if self.granularity == "coarse"

            else AGENT_REGISTRY

        )

        for domain, agent_class in registry.items():

            agent = agent_class(settings=self.settings, logger=self.logger)

            await agent.initialize()

            self._subagents[domain] = agent

            self.logger.info(f"Initialized subagent: {domain}")

        supervisor_tools = self._make_subagent_tools()

        self._tools = supervisor_tools

        self._create_react_agent(supervisor_tools)

        self.logger.info(

            f"Orchestrator initialized ({self.granularity}) with "

            f"{len(self._subagents)} subagents"

        )

    def setup_for_test_case(

        self,

        tools: list | None = None,

        **kwargs: Any,

    ) -> None:

        """Redistribute sampled tools across subagents and rebuild supervisor."""

        super().setup_for_test_case()

        if tools is None:

            return

        tool_to_domain = get_tool_to_domain_map()

        if self.granularity == "coarse":

            domain_to_group = {}

            for group_name, group_cfg in COARSE_AGENT_GROUPS.items():

                for domain in group_cfg["domains"]:

                    domain_to_group[domain] = group_name

            grouped: dict[str, list] = {name: [] for name in self._subagents}

            for t in tools:

                domain = tool_to_domain.get(t.name)

                group = domain_to_group.get(domain) if domain else None

                if group and group in grouped:

                    grouped[group].append(t)

        else:

            grouped = {name: [] for name in self._subagents}

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

        self.logger.info(f"Test case setup: {total} tools across {len(self._subagents)} subagents")

    def _make_subagent_tools(self) -> list:

        """Create one tool wrapper per subagent.

        Each tool gets a unique function name and docstring so that
        tool() derives the tool name and description from them
        (per LangChain docs).

        RunnableConfig is injected by LangGraph to propagate callbacks
        (TokenTracker, ToolTracker) to subagent LLM calls.
        """

        from langchain_core.runnables import RunnableConfig

        tools = []

        for name, subagent in self._subagents.items():

            if hasattr(subagent, 'get_available_tools') and not subagent.get_available_tools():

                continue

            description = self._get_agent_description(name)

            logger = self.logger

            async def fn(

                request: str, config: RunnableConfig,

                _agent=subagent, _name=name,

            ) -> str:

                logger.info(f"Delegating to {_name}: {request[:100]}...")

                callbacks = config.get("callbacks", None)

                try:

                    response = await _agent.chat(request, callbacks=callbacks)

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

        """Get a description for the subagent tool."""

        if self.granularity == "coarse":

            config = COARSE_AGENT_GROUPS.get(name, {})

            domains = ", ".join(config.get("domains", []))

            return f"{config.get('description', name)}. Covers: {domains}"

        desc = DOMAIN_DESCRIPTIONS.get(name, name)

        domain_tools = DOMAIN_TOOLS.get(name, [])

        tools_str = ", ".join(domain_tools[:10])

        suffix = f" +{len(domain_tools) - 10} more" if len(domain_tools) > 10 else ""

        return f"{desc}. Tools: {tools_str}{suffix}"

    def get_available_subagents(self) -> Dict[str, str]:

        """Get available subagents and their descriptions."""

        if self.granularity == "coarse":

            return {

                name: COARSE_AGENT_GROUPS[name]["description"]

                for name in self._subagents

            }

        return {

            domain: DOMAIN_DESCRIPTIONS.get(domain, "")

            for domain in self._subagents

        }

