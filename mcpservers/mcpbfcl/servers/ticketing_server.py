"""
BFCL Ticketing MCP Server.
Wraps the TicketAPI class as MCP tools for the BFCL benchmark.
"""
import json
from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.ticket_api import TicketAPI
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-ticketing")
_instance = TicketAPI()
@mcp.tool()
@safe_tool
def create_ticket(

    title: str, description: str = "", priority: int = 1
) -> Dict[str, Union[int, str]]:

    """
    Create a ticket in the system and queue it.

    Args:
        title (str): Title of the ticket.
        description (str): Description of the ticket. Defaults to an empty string.
        priority (int): Priority of the ticket, from 1 to 5. Defaults to 1. 5 is the highest priority.

    Returns:
        id (int): Unique identifier of the ticket.
        title (str): Title of the ticket.
        description (str): Description of the ticket.
        status (str): Current status of the ticket.
        priority (int): Priority level of the ticket.
    """

    return _instance.create_ticket(title=title, description=description, priority=priority)
@mcp.tool()
@safe_tool
def get_ticket(ticket_id: int) -> Dict[str, Union[int, str]]:

    """
    Get a specific ticket by its ID.

    Args:
        ticket_id (int): ID of the ticket to retrieve.

    Returns:
        id (int): Unique identifier of the ticket.
        title (str): Title of the ticket.
        description (str): Description of the ticket.
        status (str): Current status of the ticket.
        priority (int): Priority level of the ticket.
        created_by (str): Username of the ticket creator.
    """

    return _instance.get_ticket(ticket_id=ticket_id)
@mcp.tool()
@safe_tool
def close_ticket(ticket_id: int) -> Dict[str, str]:

    """
    Close a ticket.

    Args:
        ticket_id (int): ID of the ticket to be closed.

    Returns:
        status (str): Status of the close operation.
    """

    return _instance.close_ticket(ticket_id=ticket_id)
@mcp.tool()
@safe_tool
def resolve_ticket(ticket_id: int, resolution: str) -> Dict[str, str]:

    """
    Resolve a ticket with a resolution.

    Args:
        ticket_id (int): ID of the ticket to be resolved.
        resolution (str): Resolution details for the ticket.

    Returns:
        status (str): Status of the resolve operation.
    """

    return _instance.resolve_ticket(ticket_id=ticket_id, resolution=resolution)
@mcp.tool()
@safe_tool
def edit_ticket(

    ticket_id: int, updates: Dict[str, Optional[Union[str, int]]]
) -> Dict[str, str]:

    """
    Modify the details of an existing ticket.

    Args:
        ticket_id (int): ID of the ticket to be changed.
        updates (Dict): Dictionary containing the fields to be updated.
            - title (str): [Optional] New title for the ticket.
            - description (str): [Optional] New description for the ticket.
            - status (str): [Optional] New status for the ticket.
            - priority (int): [Optional] New priority for the ticket.

    Returns:
        status (str): Status of the update operation.
    """

    return _instance.edit_ticket(ticket_id=ticket_id, updates=updates)
@mcp.tool()
@safe_tool
def ticket_login(username: str, password: str) -> Dict[str, bool]:

    """
    Authenticate a user for ticket system.

    Args:
        username (str): Username of the user.
        password (str): Password of the user.

    Returns:
        success (bool): True if login was successful, False otherwise.
    """

    return _instance.ticket_login(username=username, password=password)
@mcp.tool()
@safe_tool
def ticket_get_login_status() -> Dict[str, bool]:

    """
    Get the login status of the currently authenticated user.

    Returns:
        login_status (bool): True if a user is logged in, False otherwise.
    """

    return _instance.ticket_get_login_status()
@mcp.tool()
@safe_tool
def logout() -> Dict[str, bool]:

    """
    Log out the current user.

    Returns:
        success (bool): True if logout was successful, False otherwise.
    """

    return _instance.logout()
@mcp.tool()
@safe_tool
def get_user_tickets(

    status: Optional[str] = None,
) -> List[Dict[str, Union[int, str]]]:

    """
    Get all tickets created by the current user, optionally filtered by status.

    Args:
        status (str): [Optional] Status to filter tickets by. If None, return all tickets.

    Returns:
        id (int): Unique identifier of the ticket.
        title (str): Title of the ticket.
        description (str): Description of the ticket.
        status (str): Current status of the ticket.
        priority (int): Priority level of the ticket.
        created_by (str): Username of the ticket
    """

    return _instance.get_user_tickets(status=status)
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """
    Load a scenario configuration into the ticketing system.

    Args:
        config_json (str): JSON string containing the scenario configuration.
        long_context (bool): If True, extend state with long-context data.

    Returns:
        str: "OK" on success.
    """

    _instance._load_scenario(json.loads(config_json), long_context=long_context)

    return "OK"
@mcp.tool()
def admin_get_state() -> str:

    """
    Get the current state of the ticketing system.

    Returns:
        str: JSON string of the current public state.
    """

    return json.dumps(

        {attr: val for attr, val in vars(_instance).items() if not attr.startswith("_")},

        default=str,

    )
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

