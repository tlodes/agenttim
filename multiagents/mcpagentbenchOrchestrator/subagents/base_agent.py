"""
Base agent for MCPAgentBench domain subagents.
Subclasses set DOMAIN, AGENT_NAME, and SYSTEM_PROMPT.
Inherits StatelessSubAgent for history-free chat() and verbose logging.
"""
from typing import Any, Callable, Dict, List, Optional
from langchain.agents import create_agent
from agenttim.agents.base import StatelessSubAgent
from agenttim.config.settings import Settings
from agenttim.mcpservers.mcpagentbench.domain_config import (

    DOMAIN_DESCRIPTIONS,

    BASE_PROMPT,
)
from agenttim.multiagents.mcpagentbenchOrchestrator.mcpclients import BenchMCPClient
ToolCallCallback = Callable[[str, Dict[str, Any], str], None]
class BaseBenchAgent(StatelessSubAgent):

    """Base class for all MCPAgentBench domain subagents.

    Subclasses must set:
        DOMAIN: str       - Single MCP server domain (fine-grained, e.g., "weather")
        AGENT_NAME: str   - Human-readable agent name

    Or for coarse-grained:
        DOMAINS: list[str] - Multiple MCP server domains

    All subagents share BASE_PROMPT (from the original MCPAgentBench
    paper) so that the only variable is the architecture, not the prompt.
    """

    def _get_system_prompt(self) -> str:

        """Build system prompt: shared BASE_PROMPT + short role description."""

        domains = self._get_domains()

        descs = [DOMAIN_DESCRIPTIONS.get(d, d) for d in domains]

        role = f"You are the {self.AGENT_NAME}. Domain: {'; '.join(descs)}"

        return f"{BASE_PROMPT}\n\n## Subagent Role\n{role}"

    async def _do_initialize(self) -> None:

        """Load MCP tools and create the ReAct agent."""

        domains = self._get_domains()

        self.logger.info(f"Initializing {self.AGENT_NAME} (domains: {domains})")

        self._mcp_client = BenchMCPClient(self.settings, domains=domains)

        tools = await self._mcp_client.get_tools()

        self.logger.info(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")

        self._agent = create_agent(

            self._llm,

            tools=tools,

            system_prompt=self._get_system_prompt(),

        )

