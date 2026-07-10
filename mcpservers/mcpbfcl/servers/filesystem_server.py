"""
BFCL Filesystem MCP Server.
Wraps GorillaFileSystem as MCP tools for the BFCL benchmark.
"""
import json
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.gorilla_file_system import (

    Directory,

    File,

    GorillaFileSystem,
)
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-filesystem")
_instance = GorillaFileSystem()
def _serialize(obj: object) -> object:

    """Recursively serialize Directory/File objects to dicts."""

    if isinstance(obj, File):

        return {"__type__": "File", "name": obj.name, "content": obj.content}

    if isinstance(obj, Directory):

        return {

            "__type__": "Directory",

            "name": obj.name,

            "contents": {

                k: _serialize(v) for k, v in obj.contents.items()

            },

        }

    if isinstance(obj, dict):

        return {k: _serialize(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):

        return [_serialize(v) for v in obj]

    return obj
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """Load a scenario configuration into the GorillaFileSystem instance.

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

    """Return the current public state of the GorillaFileSystem as JSON.

    Returns:
        str: JSON string of all public attributes.
    """

    state = {}

    for attr, val in vars(_instance).items():

        if attr.startswith("_"):

            continue

        state[attr] = _serialize(val)

    return json.dumps(state, default=str)
@mcp.tool()
@safe_tool
def pwd() -> str:

    """Return the current working directory path.

    Returns:
        current_working_directory (str): The current working directory path.
    """

    return json.dumps(_instance.pwd(), default=str)
@mcp.tool()
@safe_tool
def ls(a: bool = False) -> str:

    """List the contents of the current directory.

    Args:
        a (bool): [Optional] Show hidden files and directories. Defaults to False.

    Returns:
        current_directory_content (List[str]): A list of the contents of the specified directory.
    """

    return json.dumps(_instance.ls(a=a), default=str)
@mcp.tool()
@safe_tool
def cd(folder: str) -> str:

    """Change the current working directory to the specified folder.

    Args:
        folder (str): The folder of the directory to change to. You can only change one folder level at a time.

    Returns:
        current_working_directory (str): The new current working directory path.
    """

    return json.dumps(_instance.cd(folder=folder), default=str)
@mcp.tool()
@safe_tool
def mkdir(dir_name: str) -> str:

    """Create a new directory in the current directory.

    Args:
        dir_name (str): The name of the new directory at current directory. You can only create directory at current directory.
    """

    result = _instance.mkdir(dir_name=dir_name)

    return json.dumps(result, default=str)
@mcp.tool()
@safe_tool
def touch(file_name: str) -> str:

    """Create a new file of any extension in the current directory.

    Args:
        file_name (str): The name of the new file in the current directory. file_name is local to the current directory and does not allow path.
    """

    result = _instance.touch(file_name=file_name)

    return json.dumps(result, default=str)
@mcp.tool()
@safe_tool
def echo(content: str, file_name: Optional[str] = None) -> str:

    """Write content to a file at current directory or display it in the terminal.

    Args:
        content (str): The content to write or display.
        file_name (str): [Optional] The name of the file at current directory to write the content to. Defaults to None.

    Returns:
        terminal_output (str): The content if no file name is provided, or None if written to file.
    """

    result = _instance.echo(content=content, file_name=file_name)

    return json.dumps(result, default=str)
@mcp.tool()
@safe_tool
def cat(file_name: str) -> str:

    """Display the contents of a file of any extension from current directory.

    Args:
        file_name (str): The name of the file from current directory to display. No path is allowed.

    Returns:
        file_content (str): The content of the file.
    """

    return json.dumps(_instance.cat(file_name=file_name), default=str)
@mcp.tool()
@safe_tool
def find(path: str = ".", name: Optional[str] = None) -> str:

    """Find any file or directories under specific path that contain name in its file name.

    This method searches for files of any extension and directories within a specified path that match
    the given name. If no name is provided, it returns all files and directories
    in the specified path and its subdirectories.
    Note: This method performs a recursive search through all subdirectories of the given path.

    Args:
        path (str): The directory path to start the search. Defaults to the current directory (".").
        name (str): [Optional] The name of the file or directory to search for. If None, all items are returned.

    Returns:
        matches (List[str]): A list of matching file and directory paths relative to the given path.
    """

    return json.dumps(_instance.find(path=path, name=name), default=str)
@mcp.tool()
@safe_tool
def wc(file_name: str, mode: str = "l") -> str:

    """Count the number of lines, words, and characters in a file of any extension from current directory.

    Args:
        file_name (str): Name of the file of current directory to perform wc operation on.
        mode (str): Mode of operation ('l' for lines, 'w' for words, 'c' for characters).

    Returns:
        count (int): The count of the number of lines, words, or characters in the file.
        type (str): The type of unit we are counting. [Enum]: ["lines", "words", "characters"]
    """

    return json.dumps(_instance.wc(file_name=file_name, mode=mode), default=str)
@mcp.tool()
@safe_tool
def sort(file_name: str) -> str:

    """Sort the contents of a file line by line.

    Args:
        file_name (str): The name of the file appeared at current directory to sort.

    Returns:
        sorted_content (str): The sorted content of the file.
    """

    return json.dumps(_instance.sort(file_name=file_name), default=str)
@mcp.tool()
@safe_tool
def grep(file_name: str, pattern: str) -> str:

    """Search for lines in a file of any extension at current directory that contain the specified pattern.

    Args:
        file_name (str): The name of the file to search. No path is allowed and you can only perform on file at local directory.
        pattern (str): The pattern to search for.

    Returns:
        matching_lines (List[str]): Lines that match the pattern.
    """

    return json.dumps(_instance.grep(file_name=file_name, pattern=pattern), default=str)
@mcp.tool()
@safe_tool
def du(human_readable: bool = False) -> str:

    """Estimate the disk usage of a directory and its contents.

    Args:
        human_readable (bool): If True, returns the size in human-readable format (e.g., KB, MB).

    Returns:
        disk_usage (str): The estimated disk usage.
    """

    return json.dumps(_instance.du(human_readable=human_readable), default=str)
@mcp.tool()
@safe_tool
def tail(file_name: str, lines: int = 10) -> str:

    """Display the last part of a file of any extension.

    Args:
        file_name (str): The name of the file to display. No path is allowed and you can only perform on file at local directory.
        lines (int): The number of lines to display from the end of the file. Defaults to 10.

    Returns:
        last_lines (str): The last part of the file.
    """

    return json.dumps(_instance.tail(file_name=file_name, lines=lines), default=str)
@mcp.tool()
@safe_tool
def diff(file_name1: str, file_name2: str) -> str:

    """Compare two files of any extension line by line at the current directory.

    Args:
        file_name1 (str): The name of the first file in current directory.
        file_name2 (str): The name of the second file in current directory.

    Returns:
        diff_lines (str): The differences between the two files.
    """

    return json.dumps(

        _instance.diff(file_name1=file_name1, file_name2=file_name2), default=str

    )
@mcp.tool()
@safe_tool
def mv(source: str, destination: str) -> str:

    """Move a file or directory from one location to another.

    Args:
        source (str): Source name of the file or directory to move. Source must be local to the current directory.
        destination (str): The destination name to move the file or directory to. Destination must be local to the current directory and cannot be a path. If destination is not an existing directory like when renaming something, destination is the new file name.

    Returns:
        result (str): The result of the move operation.
    """

    return json.dumps(

        _instance.mv(source=source, destination=destination), default=str

    )
@mcp.tool()
@safe_tool
def rm(file_name: str) -> str:

    """Remove a file or directory.

    Args:
        file_name (str): The name of the file or directory to remove.

    Returns:
        result (str): The result of the remove operation.
    """

    return json.dumps(_instance.rm(file_name=file_name), default=str)
@mcp.tool()
@safe_tool
def rmdir(dir_name: str) -> str:

    """Remove a directory at current directory.

    Args:
        dir_name (str): The name of the directory to remove. Directory must be local to the current directory.

    Returns:
        result (str): The result of the remove operation.
    """

    return json.dumps(_instance.rmdir(dir_name=dir_name), default=str)
@mcp.tool()
@safe_tool
def cp(source: str, destination: str) -> str:

    """Copy a file or directory from one location to another.

    If the destination is a directory, the source file or directory will be copied
    into the destination directory.

    Both source and destination must be local to the current directory.

    Args:
        source (str): The name of the file or directory to copy.
        destination (str): The destination name to copy the file or directory to.
                        If the destination is a directory, the source will be copied
                        into this directory. No file paths allowed.

    Returns:
        result (str): The result of the copy operation or an error message if the operation fails.
    """

    return json.dumps(

        _instance.cp(source=source, destination=destination), default=str

    )
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

