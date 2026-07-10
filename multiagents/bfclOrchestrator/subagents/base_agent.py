"""
Base agent for BFCL domain subagents.
Subclasses set DOMAIN and AGENT_NAME.
Inherits StatelessSubAgent for history-free chat() and verbose logging.
System prompt comes from BASE_PROMPT (original BFCL paper) + role description.
"""
from typing import Any, List, Optional
from langchain.agents import create_agent
from agenttim.agents.base import StatelessSubAgent
from agenttim.config.settings import Settings
from agenttim.bfcl.domain_config import BASE_PROMPT, DOMAIN_DESCRIPTIONS
from agenttim.multiagents.bfclOrchestrator.mcpclients import BFCLMCPClient
class BaseBFCLAgent(StatelessSubAgent):

    """Base class for BFCL domain subagents.

    Subclasses must set:
        DOMAIN: str       - Domain name (e.g., "filesystem")
        AGENT_NAME: str   - Human-readable name

    System prompt is BASE_PROMPT (from original BFCL paper) + subagent role,
    matching the pattern used by MCPAgentBench's BaseBenchAgent.
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

        self._mcp_client = BFCLMCPClient(self.settings, domains=domains)

        tools = await self._mcp_client.get_tools()

        self.logger.info(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")

        self._agent = create_agent(

            self._llm,

            tools=tools,

            system_prompt=self._get_system_prompt(),

        )

