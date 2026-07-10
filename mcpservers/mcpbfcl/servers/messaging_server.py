"""
BFCL Messaging MCP Server.
Wraps MessageAPI as MCP tools for the BFCL benchmark.
"""
import json
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.message_api import MessageAPI
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-messaging")
_instance = MessageAPI()
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """Load a scenario configuration into the MessageAPI instance.

    Args:
        config_json (str): JSON string with the scenario configuration.
        long_context (bool): If True, extend state with long-context data.

    Returns:
        str: "OK" on success.
    """

    _instance._load_scenario(json.loads(config_json), long_context=long_context)

    return "OK"
@mcp.tool()
def admin_get_state() -> str:

    """Return the current public state of the MessageAPI as JSON.

    Returns:
        str: JSON string of all public attributes.
    """

    state = {

        attr: val

        for attr, val in vars(_instance).items()

        if not attr.startswith("_")

    }

    return json.dumps(state, default=str)
@mcp.tool()
@safe_tool
def list_users() -> str:

    """List all users in the workspace.

    Returns:
        user_list (List[str]): List of all users in the workspace.
    """

    return json.dumps(_instance.list_users(), default=str)
@mcp.tool()
@safe_tool
def get_user_id(user: str) -> str:

    """Get user ID from user name.

    Args:
        user (str): User name of the user.

    Returns:
        user_id (str): User ID of the user.
    """

    return json.dumps(_instance.get_user_id(user=user), default=str)
@mcp.tool()
@safe_tool
def message_login(user_id: str) -> str:

    """Log in a user with the given user ID to message application.

    Args:
        user_id (str): User ID of the user to log in.

    Returns:
        login_status (bool): True if login was successful, False otherwise.
        message (str): A message describing the result of the login attempt.
    """

    return json.dumps(_instance.message_login(user_id=user_id), default=str)
@mcp.tool()
@safe_tool
def message_get_login_status() -> str:

    """Get the login status of the current user.

    Returns:
        login_status (bool): True if the current user is logged in, False otherwise.
    """

    return json.dumps(_instance.message_get_login_status(), default=str)
@mcp.tool()
@safe_tool
def send_message(receiver_id: str, message: str) -> str:

    """Send a message to a user.

    Args:
        receiver_id (str): User ID of the user to send the message to.
        message (str): Message to be sent.

    Returns:
        sent_status (bool): True if the message was sent successfully, False otherwise.
        message_id (int): ID of the sent message.
        message (str): A message describing the result of the send attempt.
    """

    return json.dumps(

        _instance.send_message(receiver_id=receiver_id, message=message),

        default=str,

    )
@mcp.tool()
@safe_tool
def delete_message(receiver_id: str) -> str:

    """Delete the latest message sent to a receiver.

    Args:
        receiver_id (str): User ID of the user to send the message to.

    Returns:
        deleted_status (bool): True if the message was deleted successfully, False otherwise.
        receiver_id (str): ID of the receiver of the deleted message.
        message (str): A message describing the result of the deletion attempt.
    """

    return json.dumps(

        _instance.delete_message(receiver_id=receiver_id), default=str

    )
@mcp.tool()
@safe_tool
def view_messages_sent() -> str:

    """View all historical messages sent by the current user.

    Returns:
        messages (Dict): Dictionary of messages grouped by receiver. An example of the messages dictionary is {"USR001":["Hello"],"USR002":["World"]}.
    """

    return json.dumps(_instance.view_messages_sent(), default=str)
@mcp.tool()
@safe_tool
def add_contact(user_name: str) -> str:

    """Add a contact to the workspace.

    Args:
        user_name (str): User name of contact to be added.

    Returns:
        added_status (bool): True if the contact was added successfully, False otherwise.
        user_id (str): User ID of the added contact.
        message (str): A message describing the result of the addition attempt.
    """

    return json.dumps(_instance.add_contact(user_name=user_name), default=str)
@mcp.tool()
@safe_tool
def search_messages(keyword: str) -> str:

    """Search for messages containing a specific keyword.

    Args:
        keyword (str): The keyword to search for in messages.

    Returns:
        results (List[Dict]): List of dictionaries containing matching messages.
            - receiver_id (str): User ID of the receiver of the message.
            - message (str): The message containing the keyword.
    """

    return json.dumps(_instance.search_messages(keyword=keyword), default=str)
@mcp.tool()
@safe_tool
def get_message_stats() -> str:

    """Get statistics about messages for the current user.

    Returns:
        stats (Dict): Dictionary containing message statistics.
            - received_count (int): Number of messages received by the current user.
            - total_contacts (int): Total number of contacts the user has interacted with.
    """

    return json.dumps(_instance.get_message_stats(), default=str)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

