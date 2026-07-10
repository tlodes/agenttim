"""
Combined BFCL MCP server.
Hosts all 8 domain-specific MCP endpoints on a single FastAPI process.
Each domain wraps a stateful BFCL Python class with actual implementations
from the Berkeley Function Calling Leaderboard (BFCL) benchmark.
Unlike MCPAgentBench (stateless mock tools), BFCL tools are STATEFUL:
- Each domain holds a Python class instance that mutates on tool calls
- State persists across calls within a test case
- Admin tools (admin_load_scenario, admin_get_state) manage state lifecycle
Each domain is accessible via: /mcpbfcl/{domain}/mcp
Usage:
    uvicorn main:app --port 9100 --reload

    # Or from this directory:
    python main.py
"""
from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI
from agenttim.bfcl.domain_config import ALL_DOMAINS, DOMAIN_TOOLS
from servers import (

    filesystem_server,

    math_server,

    messaging_server,

    social_server,

    ticketing_server,

    trading_server,

    travel_server,

    vehicle_server,
)
_DOMAIN_SERVERS = {

    "filesystem": filesystem_server,

    "math": math_server,

    "messaging": messaging_server,

    "social": social_server,

    "ticketing": ticketing_server,

    "trading": trading_server,

    "travel": travel_server,

    "vehicle": vehicle_server,
}
_domain_mcps = []
@asynccontextmanager
async def lifespan(app: FastAPI):

    """Start all MCP session managers."""

    async with AsyncExitStack() as stack:

        for domain_mcp in _domain_mcps:

            await stack.enter_async_context(domain_mcp.session_manager.run())

        yield
app = FastAPI(title="BFCL Combined MCP Server", lifespan=lifespan)
print("Initializing BFCL MCP servers...")
for domain in ALL_DOMAINS:

    server_module = _DOMAIN_SERVERS[domain]

    domain_mcp = server_module.get_mcp()

    tool_count = len(domain_mcp._tool_manager._tools)

    expected = len(DOMAIN_TOOLS[domain]) + 2

    domain_app = domain_mcp.streamable_http_app()

    _domain_mcps.append(domain_mcp)

    app.mount(f"/mcpbfcl/{domain}", domain_app)

    print(f"  [{domain}] {tool_count} tools ({expected} expected) -> /mcpbfcl/{domain}/mcp")
print(f"\nAll {len(ALL_DOMAINS)} domains ready.")
print("MCP endpoints available at: http://localhost:9100/mcpbfcl/{domain}/mcp")
@app.get("/")
async def root():

    """Health check and domain listing."""

    return {

        "service": "BFCL Combined MCP Server",

        "stateful": True,

        "domains": {

            domain: {

                "endpoint": f"/mcpbfcl/{domain}/mcp",

                "tool_count": len(DOMAIN_TOOLS[domain]),

                "tools": DOMAIN_TOOLS[domain],

                "admin_tools": ["admin_load_scenario", "admin_get_state"],

            }

            for domain in ALL_DOMAINS

        },

        "total_tools": sum(len(t) for t in DOMAIN_TOOLS.values()),

    }
if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "main:app",

        host="0.0.0.0",

        port=9100,

        reload=False,

    )

