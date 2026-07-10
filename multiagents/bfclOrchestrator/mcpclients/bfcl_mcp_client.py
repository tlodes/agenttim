"""
MCP client for BFCL domain servers.
Connects to the combined BFCL MCP server at domain-specific endpoints.
Supports single-domain (fine-grained) and multi-domain (coarse-grained) modes.
Unlike MCPAgentBench's BenchMCPClient, this client also provides admin
methods for stateful test case management:
- load_scenario(): Reset instance state for a new test case
- get_state(): Read instance state for evaluation comparison
"""
import json
from typing import Any, List, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from agenttim.config.settings import Settings
ADMIN_TOOLS = {"admin_load_scenario", "admin_get_state"}
class BFCLMCPClient:

    """
    MCP client for one or more BFCL domain servers.

    Args:
        settings: Application settings containing MCP_BFCL_BASE_URL.
        domain: Single domain name (fine-grained mode).
        domains: List of domain names (coarse-grained mode).
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

        self._all_tools: Optional[List[BaseTool]] = None

        self._agent_tools: Optional[List[BaseTool]] = None

    def _get_url(self, domain: str) -> str:

        """Construct the MCP endpoint URL for a domain."""

        base_url = self.settings.MCP_BFCL_BASE_URL.rstrip("/")

        return f"{base_url}/mcpbfcl/{domain}/mcp"

    def _create_client(self) -> MultiServerMCPClient:

        """Create the MCP client configured for all domains."""

        config = {

            f"mcpbfcl-{domain}": {

                "transport": "streamable_http",

                "url": self._get_url(domain),

            }

            for domain in self._domains

        }

        return MultiServerMCPClient(config)

    async def get_tools(self) -> List[BaseTool]:

        """Fetch tools from MCP servers, excluding admin tools.

        Returns only the actual domain tools (not admin_load_scenario etc.).
        """

        if self._agent_tools is not None:

            return self._agent_tools

        await self._ensure_connected()

        self._agent_tools = [

            t for t in self._all_tools if t.name not in ADMIN_TOOLS

        ]

        return self._agent_tools

    async def get_all_tools(self) -> List[BaseTool]:

        """Fetch ALL tools including admin tools."""

        await self._ensure_connected()

        return self._all_tools

    async def _ensure_connected(self) -> None:

        """Connect and fetch tools if not already done."""

        if self._all_tools is not None:

            return

        self._client = self._create_client()

        self._all_tools = await self._client.get_tools()

    async def load_scenario(self, config: dict[str, Any]) -> None:

        """Reset instance state on all connected domain servers.

        Calls admin_load_scenario on each domain server with the
        relevant portion of the test case's initial_config.

        Args:
            config: The test case's initial_config dict, keyed by
                    BFCL class name (e.g., {"GorillaFileSystem": {...}}).
        """

        await self._ensure_connected()

        from agenttim.bfcl.domain_config import CLASS_TO_DOMAIN

        for tool in self._all_tools:

            if tool.name != "admin_load_scenario":

                continue

            domain = self._find_domain_for_admin_tool(tool)

            class_config = self._extract_class_config(domain, config, CLASS_TO_DOMAIN)

            config_json = json.dumps(class_config, default=str)

            await tool.ainvoke({"config_json": config_json})

    async def get_state(self) -> dict[str, Any]:

        """Read state from all connected domain servers.

        Calls admin_get_state on each domain server and returns
        a combined dict keyed by domain name.
        """

        await self._ensure_connected()

        states: dict[str, Any] = {}

        for tool in self._all_tools:

            if tool.name != "admin_get_state":

                continue

            result = await tool.ainvoke({})

            domain = self._find_domain_for_admin_tool(tool)

            if domain:

                states[domain] = json.loads(result) if isinstance(result, str) else result

        return states

    def _find_domain_for_admin_tool(self, tool: BaseTool) -> Optional[str]:

        """Determine which domain an admin tool belongs to.

        Admin tools are namespaced in MultiServerMCPClient by the
        server key prefix. Fallback: return first domain.
        """

        if hasattr(tool, "metadata") and tool.metadata:

            server_key = tool.metadata.get("server_key", "")

            for domain in self._domains:

                if domain in server_key:

                    return domain

        if len(self._domains) == 1:

            return self._domains[0]

        return None

    @staticmethod

    def _extract_class_config(

        domain: Optional[str],

        config: dict[str, Any],

        class_to_domain: dict[str, str],

    ) -> dict:

        """Extract the initial_config portion for a specific domain."""

        if domain is None:

            return {}

        for class_name, d in class_to_domain.items():

            if d == domain and class_name in config:

                return config[class_name]

        return {}

    def get_tool_names(self) -> List[str]:

        """Get names of agent-facing tools (excluding admin)."""

        if self._agent_tools is None:

            return []

        return [t.name for t in self._agent_tools]

    def get_domain_names(self) -> List[str]:

        """Get connected domain names."""

        return list(self._domains)

