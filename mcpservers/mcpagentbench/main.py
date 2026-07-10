"""
Combined MCPAgentBench MCP server.
Hosts all 16 domain-specific MCP endpoints on a single FastAPI process.
Each domain is a concrete FastMCP server with actual mock implementations
from the original MCPAgentBench benchmark files.
Each domain is accessible via: /mcpbench/{domain}/mcp
Usage:
    uvicorn main:app --port 9000 --reload

    # Or from this directory:
    python main.py
"""
from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI
from domain_config import ALL_DOMAINS, DOMAIN_TOOLS
from servers import (

    weather_server,

    travel_server,

    calendar_server,

    dining_server,

    finance_server,

    health_server,

    code_server,

    entertainment_server,

    media_server,

    data_server,

    geo_server,

    shopping_server,

    lifestyle_server,

    content_server,

    simulation_server,

    utilities_server,
)
_DOMAIN_SERVERS = {

    "weather": weather_server,

    "travel": travel_server,

    "calendar": calendar_server,

    "dining": dining_server,

    "finance": finance_server,

    "health": health_server,

    "code": code_server,

    "entertainment": entertainment_server,

    "media": media_server,

    "data": data_server,

    "geo": geo_server,

    "shopping": shopping_server,

    "lifestyle": lifestyle_server,

    "content": content_server,

    "simulation": simulation_server,

    "utilities": utilities_server,
}
_domain_mcps = []
@asynccontextmanager
async def lifespan(app: FastAPI):

    """Start all MCP session managers so their task groups are initialized."""

    async with AsyncExitStack() as stack:

        for domain_mcp in _domain_mcps:

            await stack.enter_async_context(domain_mcp.session_manager.run())

        yield
app = FastAPI(title="MCPAgentBench Combined Server", lifespan=lifespan)
print("Initializing MCPAgentBench MCP servers...")
for domain in ALL_DOMAINS:

    server_module = _DOMAIN_SERVERS[domain]

    domain_mcp = server_module.get_mcp()

    tool_count = len(domain_mcp._tool_manager._tools)

    expected = len(DOMAIN_TOOLS[domain])

    domain_app = domain_mcp.streamable_http_app()

    _domain_mcps.append(domain_mcp)

    app.mount(f"/mcpbench/{domain}", domain_app)

    print(f"  [{domain}] {tool_count}/{expected} tools -> /mcpbench/{domain}/mcp")
print(f"\nAll {len(ALL_DOMAINS)} domains ready.")
print("MCP endpoints available at: http://localhost:9000/mcpbench/{domain}/mcp")
@app.get("/")
async def root():

    """Health check and domain listing."""

    return {

        "service": "MCPAgentBench Combined MCP Server",

        "domains": {

            domain: {

                "endpoint": f"/mcpbench/{domain}/mcp",

                "tool_count": len(DOMAIN_TOOLS[domain]),

                "tools": DOMAIN_TOOLS[domain],

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

        port=9000,

        reload=False,

    )

