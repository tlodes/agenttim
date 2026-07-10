"""
MCPAgentBench Dining MCP Server.
Concrete FastMCP server with 5 tools for the dining domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-dining")
@mcp.tool()
@safe_tool
def search_restaurant(location: str, cuisineTypes: str) -> str:

    '''"""
Find restaurants based on a specified city and cuisine type.
The `location` parameter must be the name of a city only, without state, country, or additional descriptors.
For example, "Portland" is valid, but "Portland, OR" is not; "New York" is valid, but "New York City" is not.
The `cuisineTypes` parameter must be a string where each word is capitalized (e.g., "Italian", "Seafood", "Freshwater Fish"), and it must be one of the following: 'Ethiopian', 'Freshwater Fish', 'Italian', 'Seafood', 'American', 'Izakaya', 'Parisian', 'Indian', 'Chinese'.
Args:
    location (str): The name of the city to search in. Must not include state, country, or other qualifiers.
    cuisineTypes (str): The cuisine type to search for, with each word capitalized, and it must be one of the following: 'Ethiopian', 'Freshwater Fish', 'Italian', 'Seafood', 'American', 'Izakaya', 'Parisian', 'Indian', 'Chinese'.
Returns:
    str: A formatted string listing matching restaurants, or a message indicating no matches were found.
"""'''

    mock_restaurants = [{'name': 'Ethiopian Delight', 'location': 'Berkeley', 'cuisine': ['Ethiopian'], 'price_level': 2}, {'name': 'Freshwater Fishery', 'location': 'Palo Alto', 'cuisine': ['Freshwater Fish'], 'price_level': 3}, {'name': 'American Bistro', 'location': 'San Jose', 'cuisine': ['American'], 'price_level': 3}, {'name': 'Lobster Shack', 'location': 'San Mateo', 'cuisine': ['Seafood'], 'price_level': 4}, {'name': '2g Japanese Brasserie', 'location': 'San Francisco', 'cuisine': ['Izakaya', 'Japanese'], 'price_level': 3}, {'name': "Akiko's Sushi Bar", 'location': 'San Francisco', 'cuisine': ['Japanese', 'Seafood'], 'price_level': 3}, {'name': 'Marche Aux Fleurs', 'location': 'Ross', 'cuisine': ['Parisian', 'French'], 'price_level': 4}, {'name': 'Spice of India', 'location': 'Livermore', 'cuisine': ['Indian'], 'price_level': 2}, {'name': 'Mei-Don Chinese Cuisine', 'location': 'San Francisco', 'cuisine': ['Chinese'], 'price_level': 1}, {'name': 'Seafood House', 'location': 'San Bruno', 'cuisine': ['Seafood'], 'price_level': 3}]

    results = []

    for restaurant in mock_restaurants:

        if cuisineTypes in restaurant['cuisine'] and location and (restaurant['location'].lower() == location.lower()):

            results.append(restaurant)

    if not results:

        return f'No restaurants found for {cuisineTypes} cuisine in {location}.'

    formatted_results = []

    for restaurant in results:

        formatted_results.append(f"Found the following restaurant: Name: {restaurant['name']}, Location: {restaurant['location']}, Cuisine: {', '.join(restaurant['cuisine'])}, Price Level: {restaurant['price_level']}")

    return '\n'.join(formatted_results)
@mcp.tool()
@safe_tool
def get_restaurant_details(restaurant_name: str) -> str:

    '''"""
Get detailed information about a specific restaurant using its name.
Args:
    restaurant_name (str): The exact name of the restaurant to retrieve details for.
Returns:
    str: A formatted string containing the restaurant's name, address, phone number,
        liquor service availability, cuisine type, and live music availability.
        Returns an error message if the restaurant name is not found.
"""'''

    mock_restaurant_db = {'American Bistro': {'name': 'American Bistro', 'address': '1234 San Jose Ave, San Jose, CA', 'phone_number': '(408) 555-1234', 'serves_liquor': True, 'cuisine': 'American', 'live_music': False}, 'Lobster Shack': {'name': 'Lobster Shack', 'address': '5678 Ocean Blvd, San Mateo, CA', 'phone_number': '(650) 555-5678', 'serves_liquor': True, 'cuisine': 'Seafood', 'live_music': True}, 'Aato': {'name': 'Aato', 'address': '7890 Bay St, San Francisco, CA', 'phone_number': '(415) 555-7890', 'serves_liquor': True, 'cuisine': 'Japanese', 'live_music': False}, 'Union': {'name': 'Union', 'address': '1357 Market St, Santa Rosa, CA', 'phone_number': '(707) 555-1357', 'serves_liquor': True, 'cuisine': 'Italian', 'live_music': False}}

    if restaurant_name not in mock_restaurant_db:

        return 'Error: Invalid restaurant name. The restaurant details could not be found.'

    restaurant_details = mock_restaurant_db[restaurant_name]

    details = f"Restaurant Name: {restaurant_details['name']}\nAddress: {restaurant_details['address']}\nPhone Number: {restaurant_details['phone_number']}\nServes Liquor: {('Yes' if restaurant_details['serves_liquor'] else 'No')}\nCuisine: {restaurant_details['cuisine']}\nLive Music: {('Yes' if restaurant_details['live_music'] else 'No')}"

    return details
@mcp.tool()
@safe_tool
def make_reservation(restaurant_name: str) -> str:

    '''"""
Attempt to make a reservation at a specified restaurant.
This function simulates the process of creating a reservation for the given
restaurant name and returns a confirmation message.
Args:
    restaurant_name (str): The name of the restaurant where the reservation
        should be made.
Returns:
    str: A success message confirming the reservation at the specified
    restaurant.
"""'''

    return f'Success: Reservation made at {restaurant_name}.'
@mcp.tool()
@safe_tool
def search_recipes(name: str) -> str:

    '''```python
"""
Search and retrieve cooking or drink recipes from an online recipe catalog or database.
This function allows users to search for recipes by specifying a search term in the format
"xxx recipes", where "xxx" represents the type of recipes desired (e.g., "halal", "cocktail").
The search is case-insensitive and matches recipes based on their title containing the search term.
Args:
    name (str): A non-empty string specifying the type of recipes to search for, formatted as
                "xxx recipes". Examples include "halal recipes", "cocktail recipes", and
                "mocktail recipes".
Returns:
    str: A formatted string containing the details of matching recipes, including title,
         ingredients, instructions, and timing information. If no recipes are found, an error
         message is returned indicating that no matches were found for the specified search term.
Example:
    search_recipes("halal recipes")  # Returns halal cooking recipes
    search_recipes("cocktail recipes")  # Returns alcoholic drink recipes
Note:
    The search term must end with "recipes" and is case-insensitive.
"""
```'''

    if not isinstance(name, str) or not name.strip():

        return "Error: 'name' must be a non-empty string."

    mock_recipes_db = [{'title': 'Halal Chicken Biryani', 'ingredients': ['Basmati rice', 'Halal chicken', 'Onions', 'Tomatoes', 'Yogurt', 'Ginger-garlic paste', 'Spices', 'Fresh coriander'], 'instructions': 'Marinate chicken with yogurt and spices, cook with onions and tomatoes, layer with partially cooked rice, steam until done.', 'prep_time': '20 minutes', 'cook_time': '40 minutes', 'tags': ['halal', 'rice', 'main course', 'South Asian']}, {'title': 'Halal Beef Shawarma', 'ingredients': ['Halal beef', 'Pita bread', 'Garlic sauce', 'Lettuce', 'Tomatoes', 'Cucumber', 'Spices'], 'instructions': 'Marinate beef with spices, grill until tender, serve in pita bread with vegetables and garlic sauce.', 'prep_time': '15 minutes', 'cook_time': '20 minutes', 'tags': ['halal', 'Middle Eastern', 'wrap', 'street food']}, {'title': 'Classic Mojito (Non-Alcoholic)', 'ingredients': ['Fresh mint leaves', 'Lime juice', 'Sugar', 'Soda water', 'Ice'], 'instructions': 'Muddle mint leaves with sugar and lime juice, add ice, top with soda water, stir gently.', 'prep_time': '5 minutes', 'cook_time': '0 minutes', 'tags': ['mocktail', 'drink', 'refreshing', 'cocktail']}, {'title': 'Margarita Cocktail', 'ingredients': ['Tequila', 'Triple sec', 'Lime juice', 'Salt', 'Ice'], 'instructions': 'Shake tequila, triple sec, and lime juice with ice, strain into glass with salted rim.', 'prep_time': '5 minutes', 'cook_time': '0 minutes', 'tags': ['cocktail', 'drink', 'competition']}, {'title': 'Toronto Maple Leafs Blue Lagoon Cocktail', 'ingredients': ['Vodka', 'Blue curaçao', 'Lemonade', 'Ice', 'Lemon slice'], 'instructions': "Mix vodka, blue curaçao, and lemonade over ice, garnish with lemon slice. Inspired by the Toronto Maple Leafs' blue colors.", 'prep_time': '5 minutes', 'cook_time': '0 minutes', 'tags': ['cocktail', 'drink', 'themed', 'Toronto Maple Leafs', 'competition']}]

    search_term = name.strip().lower()

    if search_term.endswith('recipes'):

        base_term = search_term[:-7].strip()

    elif search_term.endswith('recipe'):

        base_term = search_term[:-6].strip()

    else:

        base_term = search_term

    if not base_term:

        return "Error: Invalid format. Please use format like 'halal recipes' or 'cocktail recipes'."

    matching_recipes = []

    for recipe in mock_recipes_db:

        if base_term in recipe['title'].lower():

            matching_recipes.append(recipe)

    if not matching_recipes:

        return f"No recipes found with '{base_term}' in the title. Please try a different search."

    output_lines = []

    for r in matching_recipes:

        output_lines.append(f"Name: {r['title']}")

        output_lines.append(f"Ingredients: {', '.join(r['ingredients'])}")

        output_lines.append(f"Instruction: {r['instructions']}")

        output_lines.append(f"Prep Time: {r['prep_time']}")

        output_lines.append(f"Cook Time: {r['cook_time']}")

        output_lines.append('-' * 50)

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def meshi_doko(LOCATION: str, BUDGET: int, query: str, conversation_id: int) -> str:

    '''```python
    """
    Provides restaurant recommendations by interfacing with Dify AI based on location, budget, and query.

    Args:
        LOCATION (str): The location where the restaurant is sought. Must be a non-empty string.
        BUDGET (int): The maximum budget in yen for the restaurant. Must be a positive integer.
        query (str): Keywords describing the type of restaurant or food desired. Must be a non-empty string.
        conversation_id (int): An integer identifier for maintaining conversation context.

    Returns:
        str: A formatted string containing restaurant recommendations that match the given criteria,
        or a message indicating no matches were found. Includes the conversation ID for context.
    """
```'''

    mock_restaurants = [{'name': 'Light Snack Heaven', 'location': 'Tokyo', 'budget_range': (500, 1500), 'type': 'light snacks', 'description': 'A cozy spot famous for its sandwiches, salads, and fresh juices.'}, {'name': 'Snack & Chat', 'location': 'Tokyo', 'budget_range': (800, 2000), 'type': 'light snacks', 'description': 'Trendy café with small plates, tapas, and light meals perfect for quick meetings.'}, {'name': 'Salalad House', 'location': 'Osaka', 'budget_range': (700, 1800), 'type': 'salad specialty', 'description': 'A popular salad restaurant known for its fresh vegetables and unique dressings.'}, {'name': 'The Bento Corner', 'location': 'Kyoto', 'budget_range': (600, 1200), 'type': 'light snacks', 'description': 'Serving traditional Japanese bento with a modern twist.'}, {'name': 'Evening Bites', 'location': 'Tokyo', 'budget_range': (1000, 3000), 'type': 'light snacks', 'description': 'Small yet elegant restaurant offering an array of evening light meals.'}]

    if not isinstance(LOCATION, str) or not LOCATION.strip():

        raise ValueError('LOCATION must be a non-empty string.')

    if not isinstance(BUDGET, int) or BUDGET <= 0:

        raise ValueError('BUDGET must be a positive integer.')

    if not isinstance(query, str) or not query.strip():

        raise ValueError('query must be a non-empty string.')

    if not isinstance(conversation_id, int):

        raise ValueError('conversation_id must be an integer.')

    query_lower = query.lower()

    matched_restaurants = []

    for restaurant in mock_restaurants:

        if restaurant['location'].lower() == LOCATION.lower() and restaurant['budget_range'][0] <= BUDGET <= restaurant['budget_range'][1] and any((keyword in restaurant['type'].lower() or keyword in restaurant['name'].lower() for keyword in query_lower.split())):

            matched_restaurants.append(restaurant)

    if not matched_restaurants:

        return f"Sorry, I couldn't find any restaurants in {LOCATION} within your budget of {BUDGET} yen matching your query '{query}'."

    response_lines = [f'Here are some restaurant recommendations in {LOCATION} within your budget of {BUDGET} yen:']

    for r in matched_restaurants:

        response_lines.append(f"- {r['name']}: {r['description']} (Type: {r['type']}, Budget range: {r['budget_range'][0]}–{r['budget_range'][1]} yen)")

    response_lines.append(f'[Conversation ID: {conversation_id} maintained for context]')

    return '\n'.join(response_lines)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

