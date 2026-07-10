"""Shared error handler for BFCL MCP server tools.
All BFCL domain servers wrap Python class methods (GorillaFileSystem,
MathAPI, etc.) that can throw exceptions on invalid input. This helper
converts exceptions to JSON error strings so the MCP response is always
valid and the ReAct loop isn't broken.
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
            return json.dumps(_instance.method(arg), default=str)
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

