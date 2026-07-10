"""Combined MCP client that connects to all 16 MCPAgentBench domain servers."""
from typing import List, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from agenttim.config.settings import Settings
from agenttim.mcpservers.mcpagentbench.domain_config import ALL_DOMAINS
class CombinedBenchMCPClient:

    """
    Client that connects to all 16 MCPAgentBench domain MCP servers.

    Combines 141 tools from weather, travel, calendar, dining, finance,
    health, code, entertainment, media, data, geo, shopping, lifestyle,
    content, simulation, and utilities domains into a single tool set.

    All domains are served by the combined MCPAgentBench server
    at different path endpoints: /mcpbench/{domain}/mcp
    """

    def __init__(self, settings: Settings):

        self.settings = settings

        self._client: Optional[MultiServerMCPClient] = None

        self._tools: Optional[List[BaseTool]] = None

    def _create_client(self) -> MultiServerMCPClient:

        """Create the MCP client with configuration for all 16 domain servers."""

        base_url = self.settings.MCP_BENCH_BASE_URL.rstrip("/")

        config = {

            f"mcpbench-{domain}": {

                "transport": "streamable_http",

                "url": f"{base_url}/mcpbench/{domain}/mcp",

            }

            for domain in ALL_DOMAINS

        }

        return MultiServerMCPClient(config)

    async def get_tools(self) -> List[BaseTool]:

        """Get all available tools from all 16 domain MCP servers."""

        if self._tools is not None:

            return self._tools

        self._client = self._create_client()

        self._tools = await self._client.get_tools()

        return self._tools

    def get_tool_names(self) -> List[str]:

        """Get names of all loaded tools."""

        if self._tools is None:

            return []

        return [tool.name for tool in self._tools]

