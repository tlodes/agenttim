"""
MCPAgentBench Shopping MCP Server.
Concrete FastMCP server with 5 tools for the shopping domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-shopping")
@mcp.tool()
@safe_tool
def get_product_by_barcode(barcode: list) -> str:

    '''```python
"""
Retrieves detailed information about food products using their barcodes.
This function accepts a list of barcodes and returns detailed information for each corresponding product.
If a barcode is invalid or not found, an appropriate error message is returned.
Args:
    barcode (list of str): A list of barcodes as strings to look up product information.
Returns:
    str: A formatted string containing detailed information for each product found, or error messages
    for barcodes that are invalid or not found.
"""
```'''

    mock_products_db = {'4902102079290': {'name': 'Salalad Dressing', 'brand': 'Kewpie', 'category': 'Salad Dressing', 'ingredients': ['Soybean oil', 'Vinegar', 'Egg yolk', 'Sugar', 'Salt', 'Mustard', 'Spices'], 'nutrition_facts': {'serving_size': '15ml', 'calories': 60, 'fat': '6g', 'carbohydrates': '1g', 'protein': '0g'}, 'origin': 'Japan', 'description': 'A light and tangy Japanese-style salad dressing that pairs well with fresh vegetables.'}, '0737628064502': {'name': 'Organic Seaweed Snack', 'brand': "Annie Chun's", 'category': 'Snack', 'ingredients': ['Seaweed', 'Sunflower oil', 'Sesame oil', 'Salt'], 'nutrition_facts': {'serving_size': '5g', 'calories': 25, 'fat': '2g', 'carbohydrates': '1g', 'protein': '1g'}, 'origin': 'South Korea', 'description': 'Crispy, roasted organic seaweed sheets with a hint of sesame flavor.'}, '8410076471305': {'name': 'Dark Chocolate 70%', 'brand': 'Lindt', 'category': 'Chocolate', 'ingredients': ['Cocoa mass', 'Sugar', 'Cocoa butter', 'Vanilla extract'], 'nutrition_facts': {'serving_size': '40g', 'calories': 240, 'fat': '18g', 'carbohydrates': '15g', 'protein': '3g'}, 'origin': 'Switzerland', 'description': 'Rich and smooth dark chocolate with 70% cocoa content.'}}

    if not isinstance(barcode, list) or not barcode:

        return 'Error: Invalid input. Please provide a non-empty list of barcodes.'

    all_results = []

    for barcode_item in barcode:

        if not isinstance(barcode_item, str) or not barcode_item.strip():

            all_results.append(f"Error: Invalid barcode '{barcode_item}' - must be a non-empty string.")

            continue

        product_info = mock_products_db.get(barcode_item.strip())

        if not product_info:

            all_results.append(f'No product found for barcode: {barcode_item}. Please check the barcode and try again.')

            continue

        product_output = f"Barcode: {barcode_item}\nProduct Name: {product_info['name']}\nBrand: {product_info['brand']}\nCategory: {product_info['category']}\nOrigin: {product_info['origin']}\nDescription: {product_info['description']}\nIngredients: {', '.join(product_info['ingredients'])}\nNutrition Facts (per {product_info['nutrition_facts']['serving_size']}):\n  Calories: {product_info['nutrition_facts']['calories']}\n  Fat: {product_info['nutrition_facts']['fat']}\n  Carbohydrates: {product_info['nutrition_facts']['carbohydrates']}\n  Protein: {product_info['nutrition_facts']['protein']}"

        all_results.append(product_output)

    return '\n\n' + '=' * 80 + '\n\n'.join(all_results)
@mcp.tool()
@safe_tool
def recommend_electronics(product_type: str) -> str:

    '''```python
    """
    Provides detailed information about electronic products, focusing on various products of a certain type of electronic product.

    Args:
        product_type (str): The type of product to retrieve information for. Should be in lowercase.

    Returns:
        str: A formatted string containing detailed information about the specified product type. This includes specifications, features, price range, and availability. If the product type is not found or invalid, an error message is returned.
    """
```'''

    mock_products_db = {'laptop': [{'name': 'Dell XPS 15 OLED', 'category': 'Laptop', 'specs': {'processor': 'Intel Core i9-13900H', 'ram': '32GB DDR5', 'storage': '1TB NVMe SSD', 'gpu': 'NVIDIA GeForce RTX 4070', 'display': '15.6-inch 4K OLED Touch, 100% AdobeRGB', 'weight': '1.9 kg', 'battery': '86Wh, up to 12 hours'}, 'features': ['Excellent color accuracy for design work', 'Premium build quality', 'Multiple Thunderbolt 4 ports', 'Wi-Fi 6E support'], 'price_range': '$2,199 - $2,499', 'availability': 'In stock at major retailers'}, {'name': 'MacBook Pro 16-inch M3 Max', 'category': 'Laptop', 'specs': {'processor': 'Apple M3 Max (12-core CPU, 30-core GPU)', 'ram': '36GB unified memory', 'storage': '1TB SSD', 'gpu': '30-core GPU', 'display': '16.2-inch Liquid Retina XDR, 1000 nits sustained brightness', 'weight': '2.16 kg', 'battery': 'Up to 22 hours'}, 'features': ['Exceptional performance for creative work', 'Outstanding display with ProMotion 120Hz', 'Excellent battery life', 'Silent operation under load'], 'price_range': '$3,199 - $3,999', 'availability': 'Available through Apple Store'}, {'name': 'ASUS ROG Zephyrus G14', 'category': 'Laptop', 'specs': {'processor': 'AMD Ryzen 9 7940HS', 'ram': '32GB DDR5', 'storage': '1TB NVMe SSD', 'gpu': 'NVIDIA GeForce RTX 4060', 'display': '14-inch QHD+ 165Hz, 100% DCI-P3', 'weight': '1.65 kg', 'battery': '76Wh, up to 8 hours'}, 'features': ['High refresh rate display for gaming', 'Compact and portable design', 'Excellent color accuracy', 'AniMe Matrix LED display on lid'], 'price_range': '$1,599 - $1,899', 'availability': 'In stock at electronics retailers'}, {'name': 'HP Spectre x360 16', 'category': 'Laptop', 'specs': {'processor': 'Intel Core i7-13700H', 'ram': '16GB DDR5', 'storage': '512GB NVMe SSD', 'gpu': 'Intel Arc A370M', 'display': '16-inch 3K+ OLED Touch, 100% DCI-P3', 'weight': '2.0 kg', 'battery': '83Wh, up to 10 hours'}, 'features': ['2-in-1 convertible design', 'Stunning OLED display', 'Premium build with gem-cut design', 'Bang & Olufsen speakers'], 'price_range': '$1,699 - $1,999', 'availability': 'Available at HP and major retailers'}], 'iphone_16': {'name': 'Apple iPhone 16 Pro Max', 'category': 'Smartphone', 'specs': {'processor': 'Apple A18 Pro', 'ram': '8GB', 'storage_options': ['256GB', '512GB', '1TB'], 'display': '6.9-inch Super Retina XDR OLED, ProMotion 120Hz', 'camera': 'Triple-lens system with 48MP main, 12MP ultra-wproduct_typee, 12MP telephoto', 'battery': 'Up to 28 hours vproduct_typeeo playback', 'connectivity': '5G, Wi‑Fi 6E, Bluetooth 5.3'}, 'features': ['Titanium frame', 'New periscope zoom lens', 'Advanced computational photography', 'USB-C with Thunderbolt support'], 'price_range': '$1,199 - $1,699 depending on storage', 'availability': 'Available through Apple Store and authorized resellers'}}

    if not isinstance(product_type, str) or not product_type.strip():

        return "Error: 'product_type' must be a non-empty string."

    products = mock_products_db.get(product_type)

    if not products:

        return f"Error: No product found with product_type '{product_type}'."

    if isinstance(products, list):

        details = 'Laptop Recommendations with Performance Specifications and Good Display Quality:\n'

        details += '=' * 80 + '\n\n'

        for (i, product) in enumerate(products, 1):

            details += f"{i}. {product['name']}\n"

            details += f"Category: {product['category']}\n"

            details += 'Specifications:\n'

            for (spec_key, spec_value) in product['specs'].items():

                details += f'  - {spec_key.capitalize()}: {spec_value}\n'

            details += 'Features:\n'

            for feature in product['features']:

                details += f'  - {feature}\n'

            details += f"Price Range: {product['price_range']}\n"

            details += f"Availability: {product['availability']}\n"

            details += '\n' + '-' * 60 + '\n\n'

    else:

        details = f"Product Name: {products['name']}\n"

        details += f"Category: {products['category']}\n"

        details += 'Specifications:\n'

        for (spec_key, spec_value) in products['specs'].items():

            details += f'  - {spec_key.capitalize()}: {spec_value}\n'

        details += 'Features:\n'

        for feature in products['features']:

            details += f'  - {feature}\n'

        details += f"Price Range: {products['price_range']}\n"

        details += f"Availability: {products['availability']}"

    return details
@mcp.tool()
@safe_tool
def user_purchase_history(customer_ids: list[str], start_date: str, end_date: str) -> str:

    '''```python
    """
    Retrieves the purchase history of specified customers within a given date range.

    This function filters and returns the purchase history for each customer ID provided,
    listing all items purchased within the specified start and end dates.

    Args:
        customer_ids (list[str]): A list of customer IDs as strings for whom the purchase history is to be retrieved.
        start_date (str): The start date of the range in ISO 8601 format (YYYY-MM-DD).
        end_date (str): The end date of the range in ISO 8601 format (YYYY-MM-DD).

    Returns:
        str: A string representation of each customer ID followed by a list of purchased items within the date range.
             Each customer's information is separated by a newline.
    """
```'''

    mock_purchase_db = {'David': [{'purchase_id': 'P1001', 'date': '2024-01-15', 'items': ['Laptop', 'Mouse'], 'total_amount': 1200.5, 'session_id': 'S001'}, {'purchase_id': 'P1002', 'date': '2024-03-10', 'items': ['Headphones'], 'total_amount': 150.0, 'session_id': 'S002'}, {'purchase_id': 'P1003', 'date': '2025-02-05', 'items': ['Keyboard', 'Monitor'], 'total_amount': 450.75, 'session_id': 'S005'}], 'Sam': [{'purchase_id': 'P2001', 'date': '2024-02-21', 'items': ['Smartphone'], 'total_amount': 899.99, 'session_id': 'S003'}, {'purchase_id': 'P2002', 'date': '2024-01-03', 'items': ['Tablet', 'Stylus'], 'total_amount': 650.0, 'session_id': 'S004'}]}

    import datetime

    if not isinstance(customer_ids, list) or not all((isinstance(cid, str) for cid in customer_ids)):

        raise ValueError('customer_ids must be a list of strings.')

    try:

        start_dt = datetime.date.fromisoformat(start_date)

        end_dt = datetime.date.fromisoformat(end_date)

    except ValueError:

        raise ValueError('start_date and end_date must be valid ISO 8601 date strings (YYYY-MM-DD).')

    if start_dt > end_dt:

        raise ValueError('start_date cannot be after end_date.')

    filtered_data = {}

    for cid in customer_ids:

        if cid in mock_purchase_db:

            filtered_purchases = [record for record in mock_purchase_db[cid] if start_dt <= datetime.date.fromisoformat(record['date']) <= end_dt]

            if filtered_purchases:

                filtered_data[cid] = filtered_purchases

    result = {}

    for (cid, purchases) in filtered_data.items():

        all_items = []

        for purchase in purchases:

            all_items.extend(purchase['items'])

        result[cid] = all_items

    output_lines = []

    for (cid, items) in result.items():

        output_lines.append(f'{cid}: {items}')

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def grocery_pickup_slots(store_code: str, pickup_date: str) -> str:

    '''"""
List available curbside pickup slots for a grocery store on a given date.
Stores maintain separate slot inventories. Slots are expressed as 1-hour windows.
The tool will only return openings that still have capacity remaining.
Args:
    store_code (str): Identifier for the grocery location (e.g., "SEA01").
    pickup_date (str): Requested pickup date in `YYYY-MM-DD` format.
Returns:
    str: A newline separated list of open slots or an error when none are free.
"""'''

    slot_inventory = {

        'SEA01': {

            '2025-11-01': {'09:00-10:00': 0, '11:00-12:00': 2, '16:00-17:00': 1},

            '2025-11-02': {'08:00-09:00': 3, '10:00-11:00': 2, '18:00-19:00': 0},

        },

        'BEL02': {

            '2025-11-01': {'12:00-13:00': 1, '14:00-15:00': 1, '19:00-20:00': 1},

            '2025-11-03': {'09:00-10:00': 2, '13:00-14:00': 0, '17:00-18:00': 2},

        },

        'KIR03': {

            '2025-11-02': {'11:00-12:00': 1, '15:00-16:00': 1},

            '2025-11-04': {'10:00-11:00': 2, '16:00-17:00': 2},

        },

    }

    if not store_code:

        return "Error: 'store_code' is required."

    if not pickup_date:

        return "Error: 'pickup_date' is required."

    store = slot_inventory.get(store_code.upper())

    if not store:

        return f"Error: Store '{store_code}' not found."

    day_slots = store.get(pickup_date)

    if not day_slots:

        return f"No pickup slots found for {pickup_date}."

    available = [window for window, capacity in day_slots.items() if capacity > 0]

    if not available:

        return f"All pickup slots are full on {pickup_date}."

    return "Available slots:\n" + "\n".join(available)
@mcp.tool()
@safe_tool
def get_best_price(product_name: str) -> str:

    '''```python
    """
    Retrieves the best price for a specified product by searching across multiple vendors and channels.

    Args:
        product_name (str): The product identifier in underscore format (e.g., "mac_air_13").
                            Input must already use underscores; names with spaces are rejected.

    Returns:
        str: A string containing the best price information, including the vendor name, price, and purchase URL.
             If the product is not found or the input is invalid, an error message is returned.
    """
```'''

    mock_product_db = {'iphone_16': {'name': 'Apple iPhone 16', 'best_price': 1099.0, 'currency': 'USD', 'purchase_channels': [{'vendor': 'Apple Store', 'url': 'https://www.apple.com/iphone-16/', 'price': 1099.0}, {'vendor': 'Best Buy', 'url': 'https://www.bestbuy.com/iphone-16', 'price': 1099.0}, {'vendor': 'Amazon', 'url': 'https://www.amazon.com/dp/B0IPHONE16', 'price': 1079.0}]}, 'mac_air_13': {'name': 'MacBook Air 13-inch M3', 'best_price': 1099.0, 'currency': 'USD', 'purchase_channels': [{'vendor': 'Apple Store', 'url': 'https://www.apple.com/macbook-air-13/', 'price': 1099.0}, {'vendor': 'Best Buy', 'url': 'https://www.bestbuy.com/macbook-air-13', 'price': 1049.0}, {'vendor': 'Amazon', 'url': 'https://www.amazon.com/dp/B0MACBOOKAIR13', 'price': 1029.0}, {'vendor': 'B&H Photo Video', 'url': 'https://www.bhphotovideo.com/macbook-air-13', 'price': 1079.0}]}, 'high_perf_graphics_laptop': {'name': 'Dell XPS 17 (2024) - High Performance', 'best_price': 2499.0, 'currency': 'USD', 'purchase_channels': [{'vendor': 'Dell Official Store', 'url': 'https://www.dell.com/xps-17', 'price': 2499.0}, {'vendor': 'Amazon', 'url': 'https://www.amazon.com/dp/B0XPS17', 'price': 2399.0}, {'vendor': 'B&H Photo Video', 'url': 'https://www.bhphotovideo.com/xps-17', 'price': 2449.0}]}}

    if not isinstance(product_name, str) or not product_name.strip():

        return 'Error: Invalid product identifier. Please provide a non-empty string.'

    normalized_product_name = product_name.strip()

    if ' ' in normalized_product_name:

        return "Error: 'product_name' must use underscores (e.g., 'mac_air_13')."

    normalized_product_name = normalized_product_name.lower()

    if normalized_product_name in mock_product_db:

        product_info = mock_product_db[normalized_product_name]

        best_channel = min(product_info['purchase_channels'], key=lambda x: x['price'])

        return f"Best price for {product_info['name']}: {product_info['currency']} {best_channel['price']:.2f} from {best_channel['vendor']} ({best_channel['url']})."

    else:

        return f"Error: No pricing information found for product ID '{product_name}'."
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

