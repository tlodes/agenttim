"""Shared error handler for MCPAgentBench MCP server tools.
All MCPAgentBench domain servers have mock tool implementations that can
throw exceptions on invalid input (KeyError, IndexError, ValueError, etc.).
This helper converts exceptions to JSON error strings so the MCP response
is always valid and the ReAct loop isn't broken.
"""
import json
import functools
from typing import Callable
def safe_tool(func: Callable) -> Callable:

    """Decorator that catches exceptions and returns JSON error strings.

    Usage:
        @mcp.tool()
        @safe_tool
        def my_tool(arg: str) -> str:
            return json.dumps(mock_data[arg])
    """

    @functools.wraps(func)

    def wrapper(*args, **kwargs):

        try:

            return func(*args, **kwargs)

        except Exception as e:

            return json.dumps({

                "error": f"{type(e).__name__}: {e}",

                "tool": func.__name__,

            })

    return wrapper

