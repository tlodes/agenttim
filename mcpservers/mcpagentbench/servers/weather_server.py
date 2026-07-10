"""
MCPAgentBench Weather MCP Server.
Concrete FastMCP server with 2 tools for the weather domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-weather")
@mcp.tool()
@safe_tool
def weather_tool(city: str, date: str) -> str:

    '''"""
Queries a WeatherService for the weather in a specified city on a given date.
The `city` parameter must contain only the name of the city without additional
qualifiers such as state, country, or descriptors. For example, "Portland" is
valid, but "Portland, OR" is not; "New York" is valid, but "New York City" is not.
The `date` parameter must be a string in the format "MM/DD".
Args:
    city (str): The name of the city to query (e.g., "London", "Chicago").
    date (str): The date to query in "MM/DD" format (e.g., "03/12").
Returns:
    str: A formatted string describing the temperature, humidity, and wind
        conditions for the specified city and date, or a message indicating
        that the requested weather data is not available.
"""'''

    mock_weather_data = {'Chicago': {'03/01': {'temperature': '5°C', 'humidity': '60%', 'wind': '15 km/h'}}, 'London': {'03/11': {'temperature': '12°C', 'humidity': '75%', 'wind': '20 km/h'}, '03/12': {'temperature': '11°C', 'humidity': '80%', 'wind': '18 km/h'}, '03/01': {'temperature': '8°C', 'humidity': '70%', 'wind': '22 km/h'}}, 'New York': {'03/12': {'temperature': '10°C', 'humidity': '65%', 'wind': '12 km/h'}, '03/13': {'temperature': '9°C', 'humidity': '68%', 'wind': '14 km/h'}}, 'San Jose': {'03/07': {'temperature': '18°C', 'humidity': '50%', 'wind': '10 km/h'}}, 'Kuala Lumpur': {'03/06': {'temperature': '30°C', 'humidity': '85%', 'wind': '5 km/h'}}}

    if city not in mock_weather_data:

        return f'Weather data for {city} is not available.'

    if date not in mock_weather_data[city]:

        return f'Weather data for {city} on {date} is not available.'

    weather_info = mock_weather_data[city][date]

    temperature = weather_info['temperature']

    humidity = weather_info['humidity']

    wind = weather_info['wind']

    return f'The weather in {city} on {date} is as follows:\nTemperature: {temperature}\nHumidity: {humidity}\nWind: {wind}'
@mcp.tool()
@safe_tool
def weather_data_retriever(start_date: str, end_date: str, range: str, location: str) -> str:

    '''```python
    """
    Retrieves historical weather data for a specified location, date range, and year range.

    Args:
        start_date (str): The start date in 'MM/DD' format (e.g., '03/01').
        end_date (str): The end date in 'MM/DD' format (e.g., '03/15').
        range (str): The range of years to retrieve data for in 'YYYY-YYYY' format (e.g., '2019-2023').
        location (str): The name of the location (e.g., 'London').

    Returns:
        str: A string containing the weather data for the specified date and year range, including temperature and precipitation details. Returns an error message if the location is not found or if the date/year formats are invalid.
    """
```'''

    mock_weather_data = {'London': {'2019': {'03/01': {'temperature': 9, 'precipitation': 5}, '03/02': {'temperature': 9.5, 'precipitation': 3}, '03/03': {'temperature': 10, 'precipitation': 4}, '03/04': {'temperature': 10.2, 'precipitation': 0}, '03/05': {'temperature': 11, 'precipitation': 2}, '03/06': {'temperature': 11.5, 'precipitation': 1}, '03/07': {'temperature': 12, 'precipitation': 5}, '03/08': {'temperature': 12.2, 'precipitation': 6}, '03/09': {'temperature': 12.5, 'precipitation': 3}, '03/10': {'temperature': 12.8, 'precipitation': 2}, '03/11': {'temperature': 13, 'precipitation': 1}, '03/12': {'temperature': 13.2, 'precipitation': 2}, '03/13': {'temperature': 13.5, 'precipitation': 3}, '03/14': {'temperature': 13.7, 'precipitation': 1}, '03/15': {'temperature': 14, 'precipitation': 0}}, '2020': {'03/01': {'temperature': 9.3, 'precipitation': 5}, '03/02': {'temperature': 9.8, 'precipitation': 3}, '03/03': {'temperature': 10.3, 'precipitation': 4}, '03/04': {'temperature': 10.5, 'precipitation': 0}, '03/05': {'temperature': 11.2, 'precipitation': 2}, '03/06': {'temperature': 11.7, 'precipitation': 1}, '03/07': {'temperature': 12.1, 'precipitation': 5}, '03/08': {'temperature': 12.3, 'precipitation': 6}, '03/09': {'temperature': 12.6, 'precipitation': 3}, '03/10': {'temperature': 12.9, 'precipitation': 2}, '03/11': {'temperature': 13.1, 'precipitation': 1}, '03/12': {'temperature': 13.3, 'precipitation': 2}, '03/13': {'temperature': 13.6, 'precipitation': 3}, '03/14': {'temperature': 13.8, 'precipitation': 1}, '03/15': {'temperature': 14.1, 'precipitation': 0}}, '2021': {'03/01': {'temperature': 9.1, 'precipitation': 5}, '03/02': {'temperature': 9.6, 'precipitation': 3}, '03/03': {'temperature': 10.1, 'precipitation': 4}, '03/04': {'temperature': 10.3, 'precipitation': 0}, '03/05': {'temperature': 11, 'precipitation': 2}, '03/06': {'temperature': 11.4, 'precipitation': 1}, '03/07': {'temperature': 11.9, 'precipitation': 5}, '03/08': {'temperature': 12.1, 'precipitation': 6}, '03/09': {'temperature': 12.4, 'precipitation': 3}, '03/10': {'temperature': 12.7, 'precipitation': 2}, '03/11': {'temperature': 12.9, 'precipitation': 1}, '03/12': {'temperature': 13.1, 'precipitation': 2}, '03/13': {'temperature': 13.4, 'precipitation': 3}, '03/14': {'temperature': 13.6, 'precipitation': 1}, '03/15': {'temperature': 13.9, 'precipitation': 0}}, '2022': {'03/01': {'temperature': 9.2, 'precipitation': 5}, '03/02': {'temperature': 9.7, 'precipitation': 3}, '03/03': {'temperature': 10.2, 'precipitation': 4}, '03/04': {'temperature': 10.4, 'precipitation': 0}, '03/05': {'temperature': 11.1, 'precipitation': 2}, '03/06': {'temperature': 11.6, 'precipitation': 1}, '03/07': {'temperature': 12, 'precipitation': 5}, '03/08': {'temperature': 12.2, 'precipitation': 6}, '03/09': {'temperature': 12.5, 'precipitation': 3}, '03/10': {'temperature': 12.8, 'precipitation': 2}, '03/11': {'temperature': 13, 'precipitation': 1}, '03/12': {'temperature': 13.2, 'precipitation': 2}, '03/13': {'temperature': 13.5, 'precipitation': 3}, '03/14': {'temperature': 13.7, 'precipitation': 1}, '03/15': {'temperature': 14, 'precipitation': 0}}, '2023': {'03/01': {'temperature': 9, 'precipitation': 5}, '03/02': {'temperature': 9.5, 'precipitation': 3}, '03/03': {'temperature': 10, 'precipitation': 4}, '03/04': {'temperature': 10.2, 'precipitation': 0}, '03/05': {'temperature': 11, 'precipitation': 2}, '03/06': {'temperature': 11.5, 'precipitation': 1}, '03/07': {'temperature': 12, 'precipitation': 5}, '03/08': {'temperature': 12.2, 'precipitation': 6}, '03/09': {'temperature': 12.5, 'precipitation': 3}, '03/10': {'temperature': 12.8, 'precipitation': 2}, '03/11': {'temperature': 13, 'precipitation': 1}, '03/12': {'temperature': 13.2, 'precipitation': 2}, '03/13': {'temperature': 13.5, 'precipitation': 3}, '03/14': {'temperature': 13.7, 'precipitation': 1}, '03/15': {'temperature': 14, 'precipitation': 0}}}}

    if location not in mock_weather_data:

        return 'Error: City not found in database.'

    try:

        (start_month, start_day) = map(int, start_date.split('/'))

        (end_month, end_day) = map(int, end_date.split('/'))

    except ValueError:

        return "Error: Invalid date format. Please use 'MM/DD'."

    try:

        (start_year, end_year) = map(int, range.split('-'))

        if start_year > end_year:

            return 'Error: Start year cannot be greater than end year.'

    except ValueError:

        return "Error: Invalid year range format. Please use 'YYYY-YYYY'."

    _builtin_range = __builtins__["range"] if isinstance(__builtins__, dict) else __builtins__.range

    weather_data = []

    for year in _builtin_range(start_year, end_year + 1):

        year_data = mock_weather_data.get(location, {}).get(str(year), {})

        for date in year_data:

            (month, day) = map(int, date.split('/'))

            if (month > start_month or (month == start_month and day >= start_day)) and (month < end_month or (month == end_month and day <= end_day)):

                weather_data.append(f"Year: {year}, Date: {date}, Temperature: {year_data[date]['temperature']}°C, Precipitation: {year_data[date]['precipitation']}mm")

    if not weather_data:

        return 'Error: No data found for the specified date range.'

    return '\n'.join(weather_data)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

