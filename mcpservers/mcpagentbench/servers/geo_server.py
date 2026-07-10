"""
MCPAgentBench Geo MCP Server.
Concrete FastMCP server with 6 tools for the geo domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-geo")
@mcp.tool()
@safe_tool
def geocalc_mcp_get_points_of_interest(city: str, category: str, radius_km: float = None) -> str:

    '''```python
"""
Find points of interest (POIs) near a specified city, optionally filtered by category and search radius.
If no POIs are found within the specified radius, the radius may be increased (default is 10 km).
The category should be a single lowercase word (hyphenated words like "child-friendly" count as one word).
If no category is specified, the default category is "general".
The `city` parameter must contain only the city name without additional qualifiers.
For example:
    - Valid: "Portland", "New York"
    - Invalid: "Portland, OR", "New York City"
Args:
    city (str): Name of the city to search in. Must be the exact city name without state, country, or other qualifiers.
    category (str): Category names to filter POIs. Each category must be a single lowercase word.
        Defaults to "general" if not provided.
    radius_km (float or str, optional): Search radius in kilometers. Defaults to 10 km if not provided or empty.
Returns:
    str: A formatted string listing the matching POIs and their details, or a message indicating no results or invalid input.
"""
```'''

    mock_database = {'Toronto': {'general': [{'name': 'CN Tower', 'type': 'Landmark', 'distance_km': 2}, {'name': 'Royal Ontario Museum', 'type': 'Museum', 'distance_km': 5}], 'child-friendly': [{'name': "Ripley's Aquarium", 'type': 'Aquarium', 'distance_km': 3}]}, 'Phoenix': {'general': [{'name': 'Desert Botanical Garden', 'type': 'Garden', 'distance_km': 10}], 'child-friendly': [{'name': 'Phoenix Zoo', 'type': 'Zoo', 'distance_km': 8}, {'name': "Children's Museum of Phoenix", 'type': 'Museum', 'distance_km': 4}]}, 'New York': {'general': [{'name': 'Statue of Liberty', 'type': 'Landmark', 'distance_km': 6}, {'name': 'Central Park', 'type': 'Park', 'distance_km': 3}], 'music': [{'name': 'Metropolitan Museum of Art', 'type': 'Rock Concert', 'distance_km': 4}]}, 'San Diego': {'general': [{'name': 'Balboa Park', 'type': 'Park', 'distance_km': 5}, {'name': 'San Diego Zoo', 'type': 'Zoo', 'distance_km': 7}]}, 'Philadelphia': {'museum': [{'name': 'Philadelphia Museum of Art', 'type': 'Museum', 'distance_km': 4}]}, 'San Francisco': {'general': [{'name': 'Golden Gate Park', 'type': 'Park', 'distance_km': 6}], 'museum': [{'name': 'San Francisco Museum of Modern Art', 'type': 'Museum', 'distance_km': 3}], 'garden': [{'name': 'San Francisco Botanical Garden', 'type': 'Garden', 'distance_km': 2}]}}

    default_radius_km = 10

    if not category:

        category = 'general'

    if not radius_km:

        radius_km = default_radius_km

    if city not in mock_database:

        return 'Invalid city. Please provide a valid city.'

    points_of_interest = []

    if city in mock_database and category in mock_database[city]:

        points_of_interest.extend([poi for poi in mock_database[city][category] if poi['distance_km'] <= radius_km])

    if not points_of_interest:

        return f'No points of interest found within {radius_km}km for the specified categories.'

    formatted_output = f'Points of Interest in {city}:\n'

    for poi in points_of_interest:

        formatted_output += f"- {poi['name']} ({poi['type']}), {poi['distance_km']}km away from the searching point\n"

    return formatted_output
@mcp.tool()
@safe_tool
def findParks(stateCode: str, park_type: str, limit: str, activities: str) -> str:

    '''```python
    """
    Search national parks by multiple criteria with simple pagination over mock data.

    This tool demonstrates filtering by state codes, keyword search across name/description, activity filters, and
    paginated output. All data is sourced from an in-memory example dataset for illustrative purposes.

    Args:
        stateCode (str): Comma-separated state codes (e.g., "CA,AZ").
        park_type (str): What type of park you want to find, should all be in lowercase, in the form of xxx park.
        limit (str): How many park per state you want to find in total, in the range [1, 50].
        activities (str): What activities you want to find in the park, should all be in lowercase.

    Returns:
        str: A formatted list of matching parks or an error/empty-result message when no matches or invalid
        parameters are provided.
    """
    ```'''

    parks_db = [

        {

            "name": "Yosemite National Park",

            "stateCode": "CA",

            "description": "Known for its waterfalls, deep valleys, grand meadows, and ancient giant sequoias.",

            "activities": ["hiking", "camping", "climbing"],

        },

        {

            "name": "Olympic National Park",

            "stateCode": "WA",

            "description": "Features diverse ecosystems from mountainous areas to rainforests and the Pacific coastline.",

            "activities": ["hiking", "camping", "wildlife watching"],

        },

        {

            "name": "Grand Canyon National Park",

            "stateCode": "AZ",

            "description": "Famous for its immense size and its intricate and colorful landscape.",

            "activities": ["hiking", "rafting"],

        },

        {

            "name": "Yellowstone National Park",

            "stateCode": "WY",

            "description": "Home to a large variety of wildlife and geothermal features like Old Faithful geyser.",

            "activities": ["hiking", "camping", "wildlife watching"],

        },

        {

            "name": "Zion National Park",

            "stateCode": "UT",

            "description": "Known for Zion Canyon's steep red cliffs and scenic views.",

            "activities": ["hiking", "camping", "climbing"],

        },

    ]

    if not stateCode or not park_type or not limit or not activities:

        return "Error: All parameters are required and must not be empty."

    try:

        limit = int(limit)

    except ValueError:

        return "Error: 'limit' must be an integer."

    if limit < 1 or limit > 50:

        return "Error: 'limit' must be between 1 and 50."

    state_codes = stateCode.split(",")

    search_activities = activities.split(",")

    filtered_parks = [

        park for park in parks_db

        if park['stateCode'] in state_codes and

        park_type.lower() in park['type'].lower() and

           any(activity in search_activities for activity in park['activities'])

    ]

    if not filtered_parks:

        return "No parks found matching the criteria."

    result = "Matching National Parks:\n"

    for park in filtered_parks:

        result += f"- {park['name']} (State: {park['stateCode']})\n  Description: {park['description']}\n  Activities: {', '.join(park['activities'])}\n\n"

    return result.strip()
@mcp.tool()
@safe_tool
def fetch_terrain_elevation(latitude: float, longitude: float, unit: str) -> str:

    '''```python
    """
    Retrieve the elevation above sea level for a specified geographic coordinate.

    This function is useful for applications in geographic analysis, topographical studies,
    agricultural modeling, and city planning. The elevation is returned in either meters
    (default) or feet, based on the specified unit.

    Args:
        latitude (float): The latitude of the geographic coordinate, must be between -90 and 90 degrees.
        longitude (float): The longitude of the geographic coordinate, must be between -180 and 180 degrees.
        unit (str): The unit of measurement for the elevation. Acceptable values are 'meters' or 'feet'.
                     Defaults to 'meters' if not specified.

    Returns:
        str: A string indicating the elevation at the given coordinate in the specified unit.
             If the input is invalid, an error message is returned.
    """
```'''

    mock_elevation_db = {(40.7128, -74.006): 10, (39.7392, -104.9903): 1609, (35.6895, 139.6917): 40, (19.4326, -99.1332): 2250, (34.0522, -118.2437): 71, (51.5074, -0.1278): 35, (48.8566, 2.3522): 35, (37.7749, -122.4194): 16}

    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):

        return "Error: 'latitude' and 'longitude' must be numbers."

    if latitude < -90 or latitude > 90:

        return "Error: 'latitude' must be between -90 and 90 decimal degrees."

    if longitude < -180 or longitude > 180:

        return "Error: 'longitude' must be between -180 and 180 decimal degrees."

    if unit is not None:

        if not isinstance(unit, str):

            return "Error: 'unit' must be a string."

        if unit.lower() not in ('meters', 'feet'):

            return "Error: 'unit' must be either 'meters' or 'feet'."

    unit_choice = unit.lower() if unit else 'meters'

    elevation_meters = mock_elevation_db.get((round(latitude, 4), round(longitude, 4)))

    if elevation_meters is None:

        elevation_meters = abs(latitude) * 5 + abs(longitude) * 0.1

        if elevation_meters > 4000:

            elevation_meters = 4000

    if unit_choice == 'feet':

        elevation_value = elevation_meters * 3.28084

        return f'Elevation at ({latitude}, {longitude}) is approximately {elevation_value:.2f} feet above sea level.'

    else:

        return f'Elevation at ({latitude}, {longitude}) is approximately {elevation_meters:.2f} meters above sea level.'
@mcp.tool()
@safe_tool
def download_osm_data(city: str, output_path: str, format: str) -> str:

    '''```python
    """
    Downloads raw OpenStreetMap (OSM) data for a specified city and saves it to a file.

    This function fetches OSM data for a given city and stores it in the specified
    output format. The data can be saved in one of the following formats: JSON, XML, or PBF.

    Args:
        city (str): The name of the city for which to download OSM data (e.g., "New York", "London").
        output_path (str): The file path where the downloaded OSM data will be saved. Should be in the format of /cityname.
        format (str): The format in which to save the OSM data. Must be one of "json", "xml", or "pbf".

    Returns:
        str: A success message confirming the download and the location where the OSM data is saved.

    Raises:
        ValueError: If any of the input parameters are invalid or the city is not supported.
        IOError: If there is an error saving the OSM data to the specified path.
    """
```'''

    mock_osm_data = {'Berlin': {'cities': ['Berlin-Mitte', 'Berlin-Kreuzberg', 'Berlin-Charlottenburg', 'Berlin-Spandau'], 'boundaries': {'postal_codes': ['10115', '10117', '10119', '10178', '10179', '10243', '10245', '10247', '10249', '10315'], 'state': 'Berlin', 'city': 'Berlin', 'total_area': 891.8, 'area_unit': 'km²'}}, 'Karlsruhe': {'cities': ['Karlsruhe'], 'boundaries': {'postal_codes': ['76131', '76133', '76135', '76137', '76139', '76149', '76185', '76187', '76189', '76199'], 'state': 'Baden-Württemberg', 'city': 'Karlsruhe', 'total_area': 173.46, 'area_unit': 'km²'}}}

    if not isinstance(city, str) or not city.strip():

        raise ValueError("Parameter 'city' must be a non-empty string.")

    if not isinstance(output_path, str) or not output_path.strip():

        raise ValueError("Parameter 'output_path' must be a non-empty string.")

    if not isinstance(format, str) or format.lower() not in ['json', 'xml', 'pbf']:

        raise ValueError("Parameter 'format' must be one of: 'json', 'xml', 'pbf'.")

    city_clean = city.strip()

    result_data = None

    if 'Berlin' in city_clean:

        result_data = {'city': city_clean, 'cities': mock_osm_data['Berlin']['cities'], 'boundaries': mock_osm_data['Berlin']['boundaries']}

    elif 'Karlsruhe' in city_clean:

        result_data = {'city': city_clean, 'cities': mock_osm_data['Karlsruhe']['cities'], 'boundaries': mock_osm_data['Karlsruhe']['boundaries']}

    else:

        raise ValueError(f'No mock OSM data found for city: {city_clean}')

    try:

        simulated_saved_content = {'format': format.lower(), 'data': result_data}

        saved_str = str(simulated_saved_content)

    except Exception as e:

        raise IOError(f'Failed to save OSM data to {output_path}: {e}')

    return f"OSM data for city '{city_clean}' downloaded in {format.upper()} format and saved to {output_path}."
@mcp.tool()
@safe_tool
def find_earthquakes(endTime: str, startTime: str, minLatitude: str, maxLatitude: str, minLongitude: str, maxLongitude: str, minmagnitude: str) -> str:

    '''```python
    """
    Search for earthquakes in a mock dataset by time range, bounding box, and minimum magnitude.

    This tool demonstrates typical geo-temporal filtering: date-time window, latitude/longitude bounding box, and
    minimum magnitude threshold. Inputs are provided as strings and parsed to appropriate numeric/time types.

    Args:
        endTime (str): End of time range in ISO-like format "YYYY-MM-DDTHH:MM:SS".
        startTime (str): Start of time range in ISO-like format "YYYY-MM-DDTHH:MM:SS".
        minLatitude (str): Minimum latitude of the earthquake.
        maxLatitude (str): Maximum latitude of the earthquake.
        minLongitude (str): Minimum longitude of the earthquake.
        maxLongitude (str): Maximum longitude of the earthquake.
        minmagnitude (str): Minimum magnitude of the earthquake.

    Returns:
        str: A formatted list of matching earthquakes or a message indicating no results or input errors.

    Raises:
        ValueError: If date parsing fails; other parsing issues are returned as error strings.
    """
    ```'''

    earthquakes = [

        {

            "id": "eq1",

            "location": "Los Angeles, USA",

            "latitude": 34.0522,

            "longitude": -118.2437,

            "magnitude": 4.5,

            "date": "2023-09-15T14:30:00"

        },

        {

            "id": "eq2",

            "location": "San Francisco, USA",

            "latitude": 37.7749,

            "longitude": -122.4194,

            "magnitude": 5.0,

            "date": "2023-09-10T11:00:00"

        },

        {

            "id": "eq3",

            "location": "Tokyo, Japan",

            "latitude": 35.6895,

            "longitude": 139.6917,

            "magnitude": 6.3,

            "date": "2023-08-25T09:45:00"

        },

        {

            "id": "eq4",

            "location": "Mexico City, Mexico",

            "latitude": 19.4326,

            "longitude": -99.1332,

            "magnitude": 4.8,

            "date": "2023-09-20T19:00:00"

        }

    ]

    from datetime import datetime

    def parse_date(date_string):

        try:

            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

        except ValueError:

            raise ValueError("Invalid date format. Please use 'YYYY-MM-DDTHH:MM:SS'.")

    try:

        start_time = parse_date(startTime)

        end_time = parse_date(endTime)

        max_latitude = float(maxLatitude)

        min_latitude = float(minLatitude)

        max_longitude = float(maxLongitude)

        min_longitude = float(minLongitude)

        min_magnitude = float(minmagnitude)

    except ValueError as e:

        return str(e)

    filtered_earthquakes = []

    for eq in earthquakes:

        eq_date = parse_date(eq["date"])

        if (min_latitude <= eq["latitude"] <= max_latitude and

            min_longitude <= eq["longitude"] <= max_longitude and

            eq_date >= start_time and eq_date <= end_time and

            eq["magnitude"] >= min_magnitude):

            filtered_earthquakes.append(eq)

    if filtered_earthquakes:

        result = "Found the following earthquakes:\n"

        for eq in filtered_earthquakes:

            result += (f"ID: {eq['id']}, Location: {eq['location']}, "

                       f"Latitude: {eq['latitude']}, Longitude: {eq['longitude']}, "

                       f"Magnitude: {eq['magnitude']}, Date: {eq['date']}\n")

    else:

        result = "No earthquakes found matching the criteria."

    return result
@mcp.tool()
@safe_tool
def maps_direction_driving_by_address(origin_address: str, destination_address: str) -> str:

    '''"""
Plans a driving route between two locations using their specific addresses.
This function generates driving directions based on the provided origin and
destination addresses. Each address should be the most specific name relevant
to the context, without including broader location details such as city, state,
or country. For example, use "Avalon Clinton" instead of
"Avalon Clinton, New York".
Args:
    origin_address (str): The specific name of the starting location
        (e.g., "Avalon Clinton").
    destination_address (str): The specific name of the destination location
        (e.g., "Metropolitan Museum of Art").
Returns:
    str: A textual description of the driving route, including key roads and
    estimated travel time, or an error message if the route cannot be determined.
"""'''

    mock_routes = {('Oakland International Airport', '123 Oakley Ave'): 'Driving route from Oakland International Airport to 123 Oakley Ave: Take I-880 N and CA-4 E. Estimated time: 50 minutes.', ('888 Fourth Street', '123 Santa Rosa Ave'): 'Driving route from 888 Fourth Street to 123 Santa Rosa Ave: Take US-101 N. Estimated time: 1 hour 30 minutes.', ('Wilmington', 'Philadelphia Museum of Art'): 'Driving route from Wilmington to Philadelphia Museum of Art: A drive of about 32 miles from Wilmington to the Philadelphia Museum of Art takes roughly 40 minutes, mostly via I-95, with your destination on the Benjamin Franklin Parkway near Eakins Oval.', ('Avalon Clinton', 'Metropolitan Museum of Art'): "Driving route from Avalon Clinton to Metropolitan Museum of Art: A straight, northbound drive up Fifth Avenue from Avalon Clinton leads you directly to The Met. It's a simple route: proceed east to Fifth, then head north along the scenic Museum Mile and arrive at the museum's entrance on the right.", ('Ridgewood', 'Metropolitan Museum of Art'): "Driving route from Ridgewood to Metropolitan Museum of Art: Driving from Ridgewood to the Met typically spans 8-8.3 miles and takes around 16 minutes. You'll head west into Manhattan—often via the Queensboro Bridge—then travel north along the East Side (FDR Drive or First Avenue), exiting near 82nd-83rd Streets and heading west to arrive at 1000 Fifth Avenue, where the museum stands", ('Tsinghua University', 'National Worker Gymnasium'): 'Driving route from Tsinghua University to National Worker Gymnasium: Take the Airport Expressway. Estimated time: 45 minutes.'}

    if not origin_address or not destination_address:

        return 'Error: Both origin and destination must be specified by address.'

    route_key = (origin_address, destination_address)

    if route_key in mock_routes:

        return mock_routes[route_key]

    else:

        return f'Error: Driving route from {origin_address} to {destination_address} not found in the mock database.'
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

