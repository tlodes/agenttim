"""
Generic MCP client for MCPAgentBench domain servers.
All domain MCP servers share the same connection pattern - only the
endpoint URL differs. This client is parameterized by domain name(s)
and constructs the URL(s) from settings.
Supports both fine-grained (1 domain) and coarse-grained (N domains) modes.
"""
from typing import List, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from agenttim.config.settings import Settings
class BenchMCPClient:

    """
    MCP client for one or more MCPAgentBench domain servers.

    Connects to the combined MCPAgentBench server at the domain-specific
    endpoint path(s). No JWT authentication needed (mock tools).

    Args:
        settings: Application settings containing MCP_BENCH_BASE_URL.
        domain: Single domain name (e.g., "weather"). Use for fine-grained mode.
        domains: List of domain names. Use for coarse-grained mode (N domains).
                 If both domain and domains are provided, domains takes precedence.
    """

    def __init__(

        self,

        settings: Settings,

        domain: Optional[str] = None,

        domains: Optional[List[str]] = None,

    ):

        self.settings = settings

        self._domains = domains or ([domain] if domain else [])

        self._client: Optional[MultiServerMCPClient] = None

        self._tools: Optional[List[BaseTool]] = None

    def _get_url(self, domain: str) -> str:

        """Construct the MCP endpoint URL for a domain."""

        base_url = self.settings.MCP_BENCH_BASE_URL.rstrip("/")

        return f"{base_url}/mcpbench/{domain}/mcp"

    def _create_client(self) -> MultiServerMCPClient:

        """Create the MCP client configured for all domains."""

        config = {

            f"mcpbench-{domain}": {

                "transport": "streamable_http",

                "url": self._get_url(domain),

            }

            for domain in self._domains

        }

        return MultiServerMCPClient(config)

    async def get_tools(self) -> List[BaseTool]:

        """
        Fetch and cache LangChain tools from all domain MCP servers.

        Returns:
            List of LangChain BaseTool instances across all domains.
        """

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

    def get_domain_names(self) -> List[str]:

        """Get the domain names this client connects to."""

        return list(self._domains)

