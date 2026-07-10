"""
Generator: Reads original MCPAgentBench tool files from OneDrive
and creates concrete per-domain FastMCP server files.
Applies:
1. Type hints from docstrings for the 20 functions missing them
2. 3 bugfixes for FastMCP compatibility (tuple returns, range shadowing)
Usage: python generate_servers.py
"""
import re
import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_root))
from mcpservers.mcpagentbench.domain_config import DOMAIN_TOOLS, ALL_DOMAINS
ONEDRIVE_SERVERS = Path(

    r"C:\Users\TimLodes\OneDrive - JUNE GmbH\Desktop\MCPAgentBench-5C16\servers"
)
OUTPUT_DIR = Path(__file__).resolve().parent / "servers"
TYPE_HINT_FIXES = {

    'weather_tool': 'city: str, date: str',

    'search_flights': 'type: str, origin: str, destination: str, departure_date: str, cabin_class: str, return_date: str = None',

    'booking_tool': 'city: str, checkinDate: str, checkoutDate: str',

    'search_rental_properties': 'location: str, property_type: str, rating: float = None',

    'get_rental_property_details': 'property_id: str',

    'search_ticketmaster': 'type: str, city: str',

    'create_event': 'subject: str, startDate: str = None, startTime: str = None, endDate: str = None, endTime: str = None, location: str = None, isMeeting: bool = False, attendees: str = None',

    'list_events': 'date: str',

    'find_free_slots': 'date: str',

    'search_restaurant': 'location: str, cuisineTypes: str',

    'get_restaurant_details': 'restaurant_name: str',

    'make_reservation': 'restaurant_name: str',

    'get_balance': 'account_type: str',

    'send_transaction': 'target: str, amount: float',

    'search_imdb': 'primary_title: str',

    'get_directors': 'imdb_id: str',

    'itunes_search': 'artist: str',

    'itunes_play_song': 'song: str',

    'geocalc_mcp_get_points_of_interest': 'city: str, category: str, radius_km: float = None',

    'maps_direction_driving_by_address': 'origin_address: str, destination_address: str',
}
PATCHES = {

    "weather_data_retriever": [

        (

            "    weather_data = []\n    for year in range(start_year, end_year + 1):",

            '    # FIX: Original bug - "range" parameter shadows built-in range()\n'

            "    _builtin_range = __builtins__[\"range\"] if isinstance(__builtins__, dict) else __builtins__.range\n"

            "    weather_data = []\n    for year in _builtin_range(start_year, end_year + 1):",

        ),

    ],

    "AudioEditor_apply_speed_adjustment": [

        (

            "        return ((sample_rate, adjusted_audio_data), status_msg)",

            "        return str(((sample_rate, adjusted_audio_data), status_msg))",

        ),

        (

            "        return (None, f'Unexpected error occurred: {str(e)}')",

            "        return str((None, f'Unexpected error occurred: {str(e)}'))",

        ),

    ],

    "AudioEditor_transcribe_audio_sync": [

        (

            "        return ('Error: Invalid audio_file parameter. Must be a non-empty string.', '', '', '')",

            "        return str(('Error: Invalid audio_file parameter. Must be a non-empty string.', '', '', ''))",

        ),

        (

            "        return (f\"Error: Audio file '{audio_file}' not found in transcription database.\", '', '', '')",

            "        return str((f\"Error: Audio file '{audio_file}' not found in transcription database.\", '', '', ''))",

        ),

        (

            "    return (status, data['full_text'], segments_formatted.strip(), json_formatted)",

            "    return str((status, data['full_text'], segments_formatted.strip(), json_formatted))",

        ),

    ],

    "CafChem_ADME_calc_adme": [

        (

            "    return (adme_text, props['image'])",

            "    return str((adme_text, props['image']))",

        ),

    ],
}
def extract_tool_function(file_path: Path) -> str:

    """Extract the tool function code from an original MCPAgentBench file."""

    content = file_path.read_text(encoding="utf-8")

    match = re.search(r"(@mcp\.tool\(\).*?)(?=\nif __name__|$)", content, re.DOTALL)

    if match:

        return match.group(1).rstrip()

    return f"# WARNING: Could not extract tool from {file_path.name}"
def extract_imports(file_path: Path) -> list[str]:

    """Extract non-mcp import statements from before @mcp.tool()."""

    content = file_path.read_text(encoding="utf-8")

    imports = []

    for line in content.split("\n"):

        stripped = line.strip()

        if stripped.startswith("@mcp.tool"):

            break

        if stripped.startswith("import ") or stripped.startswith("from "):

            if "fastmcp" in stripped or "mcp" in stripped.split()[1]:

                continue

            imports.append(stripped)

    return imports
def find_tool_file(tool_name: str) -> Path | None:

    direct = ONEDRIVE_SERVERS / f"{tool_name}.py"

    if direct.exists():

        return direct

    for f in ONEDRIVE_SERVERS.glob("*.py"):

        if f.stem.lower() == tool_name.lower():

            return f

    return None
def generate_domain_server(domain: str, tool_names: list[str]) -> str:

    tool_blocks = []

    all_imports = set()

    for tool_name in tool_names:

        file_path = find_tool_file(tool_name)

        if file_path is None:

            tool_blocks.append(f"\n# WARNING: File not found for tool '{tool_name}'\n")

            continue

        imports = extract_imports(file_path)

        all_imports.update(imports)

        func_code = extract_tool_function(file_path)

        if tool_name in TYPE_HINT_FIXES:

            orig_match = re.search(rf"def {tool_name}\(([^)]*)\)", func_code)

            if orig_match:

                func_code = func_code.replace(

                    f"def {tool_name}({orig_match.group(1)})",

                    f"def {tool_name}({TYPE_HINT_FIXES[tool_name]})",

                )

        if tool_name in PATCHES:

            for old, new in PATCHES[tool_name]:

                func_code = func_code.replace(old, new)

        tool_blocks.append(f"\n\n{func_code}")

    imports_section = ""

    if all_imports:

        imports_section = "\n".join(sorted(all_imports)) + "\n"

    header = f'''"""
MCPAgentBench {domain.title()} MCP Server.
Concrete FastMCP server with {len(tool_names)} tools for the {domain} domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
{imports_section}
mcp = FastMCP("mcpbench-{domain}")
'''

    body = "\n".join(tool_blocks)

    footer = '''
def get_mcp() -> FastMCP:
    """Return the FastMCP server instance for mounting in combined server."""
    return mcp
if __name__ == "__main__":
    mcp.run(transport="stdio")
'''

    return header + body + footer
def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "__init__.py").write_text(

        '"""MCPAgentBench concrete domain MCP servers."""\n', encoding="utf-8"

    )

    total_tools = 0

    for domain in ALL_DOMAINS:

        tool_names = DOMAIN_TOOLS[domain]

        missing = [t for t in tool_names if find_tool_file(t) is None]

        if missing:

            print(f"  WARNING [{domain}]: Missing files for: {missing}")

        content = generate_domain_server(domain, tool_names)

        filename = f"{domain}_server.py"

        (OUTPUT_DIR / filename).write_text(content, encoding="utf-8")

        found = len(tool_names) - len(missing)

        total_tools += found

        print(f"  [{domain}] Created {filename} ({found}/{len(tool_names)} tools)")

    print(f"\nDone! Generated {len(ALL_DOMAINS)} server files")

    print(f"Total tools: {total_tools}/141")
if __name__ == "__main__":

    main()

