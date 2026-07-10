"""
MCPAgentBench Travel MCP Server.
Concrete FastMCP server with 5 tools for the travel domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-travel")
@mcp.tool()
@safe_tool
def search_flights(type: str, origin: str, destination: str, departure_date: str, cabin_class: str, return_date: str = None) -> str:

    '''"""
Search for flights based on the specified parameters.
Supports `one_way`, `round_trip`, and `multi_city` flight types.
Dates must be provided in the `MM/DD` format.
Origin and destination must be valid IATA airport codes (e.g., `"SFO"`).
For `round_trip` flights, both `departure_date` and `return_date` are required.
Do not generate or assume dates that are not explicitly provided.
Args:
    type (str): The type of flight. One of `"one_way"`, `"round_trip"`, or `"multi_city"`.
    origin (str): IATA code of the departure airport (e.g., `"SFO"`). Set origin to "JFK" if the user departs from New York.
    destination (str): IATA code of the arrival airport (e.g., `"JFK"`). Set destination to "JFK" if the user arrives in New York.
    departure_date (str): Departure date in `MM/DD` format.
    return_date (str): Return date in `MM/DD` format. Required for `round_trip` flights; ignored for `one_way` and `multi_city`.
    cabin_class (str): Cabin class for the flight (e.g., `"economy"`, `"business"`).
Returns:
    str: A message indicating either the matching flights found or an error/empty result message.
"""'''

    flights_db = [{'origin': 'SFO', 'destination': 'YYZ', 'departure_date': '10/01', 'return_date': '10/05', 'cabin_class': 'economy', 'type': 'round_trip', 'flights': [{'flight_no': 'AC123', 'departure_time': '10/01T18:00', 'arrival_time': '10/02T02:00', 'connections': 0}, {'flight_no': 'AC456', 'departure_time': '10/05T12:00', 'arrival_time': '10/05T20:00', 'connections': 0}]}, {'origin': 'SEA', 'destination': 'PHX', 'departure_date': '03/05', 'return_date': '03/07', 'cabin_class': 'economy', 'type': 'round_trip', 'flights': [{'flight_no': 'DL789', 'departure_time': '03/05T08:00', 'arrival_time': '03/05T11:00', 'connections': 0}, {'flight_no': 'DL012', 'departure_time': '03/07T14:00', 'arrival_time': '03/07T17:00', 'connections': 0}]}, {'origin': 'PHX', 'destination': 'JFK', 'departure_date': '10/07', 'return_date': '10/14', 'cabin_class': 'economy', 'type': 'round_trip', 'flights': [{'flight_no': 'AA345', 'departure_time': '10/07T15:00', 'arrival_time': '10/07T23:00', 'connections': 0}, {'flight_no': 'AA678', 'departure_time': '10/14T09:00', 'arrival_time': '10/14T17:00', 'connections': 0}]}, {'origin': 'SEA', 'destination': 'SAN', 'departure_date': '03/04', 'return_date': '03/06', 'cabin_class': 'economy', 'type': 'round_trip', 'flights': [{'flight_no': 'UA234', 'departure_time': '03/04T07:00', 'arrival_time': '03/04T10:00', 'connections': 0}, {'flight_no': 'UA567', 'departure_time': '03/06T18:00', 'arrival_time': '03/06T21:00', 'connections': 0}]}, {'origin': 'LAX', 'destination': 'SFO', 'departure_date': '03/03', 'return_date': '03/12', 'cabin_class': 'economy', 'type': 'round_trip', 'flights': [{'flight_no': 'UA234', 'departure_time': '03/03T08:00', 'arrival_time': '03/03T09:30', 'connections': 0}, {'flight_no': 'UA567', 'departure_time': '03/12T18:00', 'arrival_time': '03/12T19:30', 'connections': 0}]}, {'origin': 'ATL', 'destination': 'PHX', 'departure_date': '03/11', 'return_date': '03/15', 'cabin_class': 'economy', 'type': 'one_way', 'flights': [{'flight_no': 'AA890', 'departure_time': '03/11T09:00', 'arrival_time': '03/10T12:00', 'connections': 0}, {'flight_no': 'AA123', 'departure_time': '03/11T14:00', 'arrival_time': '03/15T17:00', 'connections': 0}]}]

    if type not in ['one_way', 'round_trip', 'multi_city']:

        return 'Error: Invalid flight type.'

    if not origin or not destination:

        return 'Error: Origin and destination must be provided.'

    if not departure_date:

        return 'Error: Departure date must be provided.'

    if type == 'round_trip' and (not return_date):

        return 'Error: Return date must be provided for round-trip flights.'

    matching_flights = [flight for flight in flights_db if flight['origin'] == origin and flight['destination'] == destination and (flight['departure_date'] == departure_date) and (flight['return_date'] == return_date if type == 'round_trip' else True) and (flight['cabin_class'].lower() == cabin_class.lower() if cabin_class else True)]

    if not matching_flights:

        return 'No flights found for the given parameters.'

    return 'Found the following flights: ' + '\n'.join(['Departure Flight: ' + flight['flights'][0]['flight_no'] + '; Return Flight: ' + flight['flights'][1]['flight_no'] for flight in matching_flights])
@mcp.tool()
@safe_tool
def booking_tool(city: str, checkinDate: str, checkoutDate: str) -> str:

    '''"""
Books hotels in a specified city for given check-in and check-out dates.
This tool connects to the Booking MCP Server to reserve accommodations.
The `checkinDate` and `checkoutDate` must be provided in the format `MM/DD`.
Do not fabricate dates if they are not provided. The `city` parameter must
contain only the city name without state, province, or country information.
For example, "Portland" is valid, but "Portland, OR" is not; "New York" is
valid, but "New York City" is not.
Args:
    city (str): Name of the city where the hotel should be booked. Must be a
        plain city name without additional location qualifiers.
    checkinDate (str): Check-in date in `MM/DD` format.
    checkoutDate (str): Check-out date in `MM/DD` format.
Returns:
    str: A confirmation message with booking details if successful, or an
    error message if the booking could not be completed.
"""'''

    hotels_db = {'Chicago': [{'name': 'Chicago Grand Hotel', 'address': '123 Grand Ave, Chicago, IL', 'phone': '123-456-7890'}, {'name': 'Windy City Inn', 'address': '456 Windy St, Chicago, IL', 'phone': '987-654-3210'}], 'London': [{'name': 'London Bridge Hotel', 'address': 'London Bridge St, London', 'phone': '020-7946-0958'}, {'name': 'The Royal London', 'address': '123 Royal Rd, London', 'phone': '020-7946-0959'}], 'New York': [{'name': 'NYC Central Hotel', 'address': '789 Broadway, New York, NY', 'phone': '212-555-0198'}, {'name': 'Times Square Suites', 'address': '456 Seventh Ave, New York, NY', 'phone': '212-555-0199'}], 'Vancouver': [{'name': 'Vancouver Harbor Hotel', 'address': '789 Harbor St, Vancouver, BC', 'phone': '604-123-4567'}, {'name': 'Downtown Vancouver Inn', 'address': '321 Downtown Rd, Vancouver, BC', 'phone': '604-765-4321'}], 'Los Angeles': [{'name': 'LA Sunset Hotel', 'address': '123 Sunset Blvd, Los Angeles, CA', 'phone': '310-555-0101'}, {'name': 'Hollywood Inn', 'address': '456 Hollywood Rd, Los Angeles, CA', 'phone': '310-555-0102'}], 'Seattle': [{'name': 'Seattle Sky Hotel', 'address': '789 Rainy Ave, Seattle, WA', 'phone': '206-555-0145'}, {'name': 'Emerald City Inn', 'address': '321 Emerald St, Seattle, WA', 'phone': '206-555-0146'}]}

    if not city or not checkinDate or (not checkoutDate):

        return "Error: 'city', 'checkinDate', and 'checkoutDate' are required parameters."

    if city not in hotels_db:

        return f"Error: No hotels found for city '{city}'."

    hotel = hotels_db[city][0]

    booking_info = f"Booking successful!\nHotel: {hotel['name']}\nAddress: {hotel['address']}\nPhone: {hotel['phone']}\nCheck-in Date: {checkinDate}\nCheck-out Date: {checkoutDate}"

    return booking_info
@mcp.tool()
@safe_tool
def search_rental_properties(location: str, property_type: str, rating: float = None) -> str:

    '''"""
Search for rental listings based on specified criteria, including city name, property type, and optional minimum rating.
The `location` parameter must contain only the name of a city (e.g., "Portland" is valid, but "Portland, OR" is not; "New York" is valid, but "New York City" is not). The `property_type` must be provided in lowercase (e.g., "house", "apartment"). If `rating` is provided, only properties with a rating greater than or equal to this value will be returned.
Args:
    location (str): Name of the city where the property is located. Must not include state, country, or other qualifiers.
    property_type (str): Type of property in lowercase (e.g., "house", "apartment").
    rating (float, optional): Minimum acceptable property rating. Defaults to None.
Returns:
    str: A formatted string listing matching properties, or a message indicating no matches were found.
"""'''

    rental_properties_db = [{'location': 'New York', 'property_type': 'house', 'rating': 4.0, 'property_id': 'NY123', 'address': '123 New York Ave'}, {'location': 'Paris', 'property_type': 'house', 'rating': 4.5, 'property_id': 'PAR456', 'address': '123 Paris Ave'}, {'location': 'San Francisco', 'property_type': 'house', 'rating': 4.3, 'property_id': 'SF789', 'address': '123 San Francisco Ave'}, {'location': 'Oakley', 'property_type': 'apartment', 'rating': 4.2, 'property_id': 'OAK123', 'address': '123 Oakley Ave'}, {'location': 'Santa Rosa', 'property_type': 'apartment', 'rating': 4.1, 'property_id': 'SRO123', 'address': '123 Santa Rosa Ave'}, {'location': 'London', 'property_type': 'house', 'rating': 4.4, 'property_id': 'LN987', 'address': '123 London Ave'}]

    filtered_properties = []

    if not rating:

        for property in rental_properties_db:

            if location and property['location'].lower() == location.lower() and (property['property_type'] == property_type):

                filtered_properties.append(property)

    else:

        for property in rental_properties_db:

            if location and property['location'].lower() == location.lower() and (property['property_type'] == property_type) and (property['rating'] >= float(rating)):

                filtered_properties.append(property)

    response = ''

    if filtered_properties:

        for prop in filtered_properties:

            response += f"Type: {prop['property_type']}, Rating: {prop['rating']}, Property ID: {prop['property_id']}, Address: {prop['address']}\n"

    else:

        response = 'No properties found matching the criteria.'

    return response
@mcp.tool()
@safe_tool
def get_rental_property_details(property_id: str) -> str:

    '''"""
Retrieve detailed information about a specific rental property using its unique ID.
Args:
    property_id (str): The unique identifier of the rental property.
        For example, 'NY123' or 'PAR456'.
Returns:
    str: A formatted string containing the property's details, including
        location, description, capacity, available dates, price per night,
        contact number, and availability of laundry service and air conditioning.
        Returns an error message if the property_id is missing or not found.
"""'''

    mock_rental_properties = {'NY123': {'location': 'New York', 'description': 'Cozy house with laundry service, perfect for small families.', 'capacity': 2, 'available_date': 'Monday the 4th to Saturday the 9th', 'price_per_night': 150, 'contact_number': '+1-415-123-4567', 'laundry_service': True, 'air_conditioning': False}, 'PAR456': {'location': 'Paris', 'description': 'Charming studio in the heart of Paris, ideal for solo travelers.', 'capacity': 1, 'available_date': '1st to 11th', 'price_per_night': 100, 'contact_number': '+33-1-2345-6789', 'laundry_service': False, 'air_conditioning': True}, 'SF789': {'location': 'San Francisco', 'description': 'Spacious house, great for groups, includes laundry service.', 'capacity': 5, 'available_date': 'March 2nd', 'price_per_night': 200, 'contact_number': '+1-415-987-6543', 'laundry_service': True, 'air_conditioning': True}, 'LN987': {'location': 'London', 'description': 'Modern apartment with all amenities, suited for single travelers.', 'capacity': 1, 'available_date': '1st to 4th', 'price_per_night': 120, 'contact_number': '+44-20-7946-0958', 'laundry_service': False, 'air_conditioning': True}}

    if not property_id:

        return 'Error: No property_id provided.'

    property_details = mock_rental_properties.get(property_id)

    if not property_details:

        return f"Error: Property with ID '{property_id}' not found."

    response = f"Property ID: {property_id}\nLocation: {property_details['location']}\nDescription: {property_details['description']}\nCapacity: {property_details['capacity']} persons\nAvailable Date: {property_details['available_date']}\nPrice per Night: ${property_details['price_per_night']}\nContact Number: {property_details['contact_number']}\nLaundry Service: {('Yes' if property_details['laundry_service'] else 'No')}\nAir Conditioning: {('Yes' if property_details['air_conditioning'] else 'No')}"

    return response
@mcp.tool()
@safe_tool
def search_ticketmaster(type: str, city: str) -> str:

    '''```python
"""
Search for events based on event type and city location.
The `type` parameter must be formatted with each word capitalized and the word
"Event" appended at the end, and only containing two words in total. For example: "Concert Event".
The `city` parameter should contain only the city name without state or country
information. For example: "Portland" is valid, but "Portland, OR" is not.
Args:
    type (str): The event type to search for, with each word capitalized and
        ending with "Event", containing and only containing two words in total (e.g., "Concert Event").
    city (str): The name of the city where the event is located, without state
        or country (e.g., "Seattle").
Returns:
    str: A formatted string listing the matching events, including event type,
    location, and date range.
"""
```'''

    mock_db = [{'event type': 'Concert Event', 'event location': 'San Francisco', 'start date': '03/01', 'end date': '03/02'}, {'event type': 'Football Event', 'event location': 'Boston', 'start date': '04/06', 'end date': '04/06'}, {'event type': 'Concert Event', 'event location': 'Rohnert Park', 'start date': '03/11', 'end date': '03/11'}, {'event type': 'Country Event', 'event location': 'Seattle', 'start date': '04/10', 'end date': '04/10'}, {'event type': 'Pop Event', 'event location': 'London', 'start date': '05/09', 'end date': '05/09'}, {'event type': 'Basketball Event', 'event location': 'Atlanta', 'start date': '03/05', 'end date': '03/05'}, {'event type': 'Football Event', 'event location': 'Atlanta', 'start date': '03/13', 'end date': '03/13'}, {'event type': 'Rock Event', 'event location': 'New York', 'start date': '03/11', 'end date': '03/11'}, {'event type': 'Match Event', 'event location': 'Portland', 'start date': '03/06', 'end date': '03/06'}, {'event type': 'Baseball Event', 'event location': 'New York', 'start date': '03/13', 'end date': '03/13'}, {'event type': 'Concert Event', 'event location': 'Washington', 'start date': '03/07', 'end date': '03/07'}]

    results = [event for event in mock_db if type in event['event type'] and city.lower() == event['event location'].lower()]

    return 'Found the following events: ' + '\n'.join([event['event type'] + ' in ' + event['event location'] + ' on ' + event['start date'] + ' to ' + event['end date'] for event in results])
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

