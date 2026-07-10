"""
MCPAgentBench Utilities MCP Server.
Concrete FastMCP server with 25 tools for the utilities domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from typing import Union, List
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-utilities")
@mcp.tool()
@safe_tool
def connect_database(database_name: str) -> str:

    '''```python
    """
    Establishes a secure, reusable connection to a relational database using a provider registry and secret-managed credentials.
    The function creates or retrieves a pooled, TLS-enabled connection based on the specified database name, applying best-practice
    defaults such as TLS/SSL where available, least-privilege users, and parameterized queries.

    Args:
        database_name (str): The name of the database to connect to. Must be a non-empty string.

    Returns:
        str: A message indicating whether the connection was successful or not. In case of success, it specifies readiness for
        secure operations. In case of failure, it provides an error message detailing the issue.
    """
```'''

    provider_registry = {'movie_reviews_db': {'provider': 'mysql', 'host': 'movies.example.com', 'port': 3306, 'tls': True, 'user': 'movie_app_user', 'required_ssl': True}, 'online_learning_db': {'provider': 'postgresql', 'host': 'learning.example.com', 'port': 5432, 'tls': True, 'user': 'learning_app_user', 'required_ssl': True}}

    secret_manager = {'movie_app_user': {'password': 'secureMoviePass123!', 'permissions': ['read_reviews', 'write_reviews']}, 'learning_app_user': {'password': 'secureLearnPass456!', 'permissions': ['read_students', 'update_progress']}}

    if not isinstance(database_name, str) or not database_name.strip():

        return 'Error: Invalid database_name parameter. Please provide a non-empty string.'

    db_name = database_name.strip()

    if db_name not in provider_registry:

        return f"Error: Database '{db_name}' not found in provider registry."

    config = provider_registry[db_name]

    user_creds = secret_manager.get(config['user'])

    try:

        if config.get('required_ssl') and (not config.get('tls')):

            return f"Error: Database '{db_name}' requires TLS/SSL but it is not enabled."

        if not user_creds or 'password' not in user_creds:

            return f"Error: Missing credentials for user '{config['user']}'."

        connection_pool = f"Pool({config['provider']}://{config['user']}@{config['host']}:{config['port']}/{db_name})"

        if db_name == 'movie_reviews_db':

            return "Successfully connected to 'movie_reviews_db' with TLS-enabled pooled connection. Ready for secure movie review operations."

        elif db_name == 'online_learning_db':

            return "Successfully connected to 'online_learning_db' with TLS-enabled pooled connection. Ready for secure student data operations."

        else:

            return f"Successfully connected to '{db_name}' with secure pooled connection."

    except Exception as e:

        return f"Error: Failed to connect to '{db_name}'. Details: {str(e)}"
@mcp.tool()
@safe_tool
def Connect_SQL_Server(connectionString: int) -> str:

    '''```python
    """
    Establish a connection to a SQL Server using a specified connection profile ID.

    Args:
        connectionString (int): An integer representing the connection profile ID
            for the SQL Server. This ID corresponds to a predefined connection
            profile.

    Returns:
        str: A message indicating the success or failure of the connection attempt.
        If successful, returns a message confirming the connection to the SQL Server
        with the profile description. If unsuccessful, returns an error message
        detailing the issue.
    """
```'''

    if not isinstance(connectionString, int):

        return 'Error: connectionString must be an integer representing a mock connection profile ID.'

    mock_connection_profiles = {1: {'description': 'Local development SQL Server instance', 'connection_string': 'Data Source=localhost;Initial Catalog=master;Integrated Security=True;', 'status': 'connected'}, 2: {'description': 'Amazon RDS SQL Server - Production', 'connection_string': 'Data Source=rds-prod.company.com;Initial Catalog=prod_db;User ID=admin;Password=***;', 'status': 'connected'}, 3: {'description': 'Amazon RDS SQL Server - Staging', 'connection_string': 'Data Source=rds-staging.company.com;Initial Catalog=staging_db;User ID=staging;Password=***;', 'status': 'connected'}}

    if connectionString not in mock_connection_profiles:

        return f'Error: No connection profile found for ID {connectionString}.'

    profile = mock_connection_profiles[connectionString]

    try:

        if profile['status'] == 'connected':

            return f"Successfully connected to SQL Server: {profile['description']}"

        else:

            return f"Error: Unable to connect to SQL Server: {profile['description']}"

    except Exception as e:

        return f'Error: An unexpected error occurred while connecting to the SQL Server. Details: {str(e)}'
@mcp.tool()
@safe_tool
def mongo_mcp(mongoUri: str, collection_name: str) -> str:

    '''```python
    """
    A tool that enables querying of a MongoDB database using natural language via MCP.

    Args:
        mongoUri (str): A non-empty string representing the MongoDB connection URI, should be as detail as possible.
        collection_name (str): A non-empty string specifying the name of the collection to query.

    Returns:
        str: A formatted string containing the retrieved data from the specified collection.
        If the database or collection is not found, an error message is returned.
    """
```'''

    if not isinstance(mongoUri, str) or not mongoUri.strip():

        raise ValueError('Invalid mongoUri: must be a non-empty string representing the MongoDB connection string.')

    if not isinstance(collection_name, str) or not collection_name.strip():

        raise ValueError('Invalid collection_name: must be a non-empty string representing the collection name.')

    customers_collection = [{'name': 'Ocean', 'postal_code': '90210', 'email': 'ocean@example.com', 'phone': '555-1234'}, {'name': 'Alice', 'postal_code': '10001', 'email': 'alice@example.com', 'phone': '555-5678'}, {'name': 'Bob', 'postal_code': '30301', 'email': 'bob@example.com', 'phone': '555-8765'}]

    products_collection = [{'product_name': 'Laptop', 'category': 'Electronics', 'price': 1200.5, 'yearly_sales': [{'year': '2023', 'units_sold': 120, 'revenue': 144060.0}, {'year': '2024', 'units_sold': 180, 'revenue': 216090.0}, {'year': '2025', 'units_sold': 240, 'revenue': 288120.0}]}, {'product_name': 'Mouse', 'category': 'Electronics', 'price': 25.0, 'yearly_sales': [{'year': '2023', 'units_sold': 480, 'revenue': 12000.0}, {'year': '2024', 'units_sold': 600, 'revenue': 15000.0}, {'year': '2025', 'units_sold': 720, 'revenue': 18000.0}]}, {'product_name': 'Headphones', 'category': 'Electronics', 'price': 150.0, 'yearly_sales': [{'year': '2023', 'units_sold': 96, 'revenue': 14400.0}, {'year': '2024', 'units_sold': 144, 'revenue': 21600.0}, {'year': '2025', 'units_sold': 192, 'revenue': 28800.0}]}, {'product_name': 'Smartphone', 'category': 'Electronics', 'price': 899.99, 'yearly_sales': [{'year': '2023', 'units_sold': 60, 'revenue': 53999.4}, {'year': '2024', 'units_sold': 90, 'revenue': 80999.1}, {'year': '2025', 'units_sold': 120, 'revenue': 107998.8}]}, {'product_name': 'Tablet', 'category': 'Electronics', 'price': 600.0, 'yearly_sales': [{'year': '2023', 'units_sold': 36, 'revenue': 21600.0}, {'year': '2024', 'units_sold': 54, 'revenue': 32400.0}, {'year': '2025', 'units_sold': 72, 'revenue': 43200.0}]}, {'product_name': 'Stylus', 'category': 'Accessories', 'price': 50.0, 'yearly_sales': [{'year': '2023', 'units_sold': 120, 'revenue': 6000.0}, {'year': '2024', 'units_sold': 180, 'revenue': 9000.0}, {'year': '2025', 'units_sold': 240, 'revenue': 12000.0}]}]

    mock_databases = {'mongodb://localhost:27017/customers_db': {'customers': customers_collection}, 'mongodb://localhost:27017/product_detail': {'products': products_collection}}

    if mongoUri not in mock_databases:

        return f"Database '{mongoUri}' not found in mock databases."

    if collection_name not in mock_databases[mongoUri]:

        return f"Collection '{collection_name}' not found in database '{mongoUri}'."

    collection_data = mock_databases[mongoUri][collection_name]

    if collection_name == 'customers':

        customer_list = []

        for customer in collection_data:

            customer_list.append(f"Name: {customer['name']}, Postal Code: {customer['postal_code']}, Email: {customer['email']}, Phone: {customer['phone']}")

        return f"Retrieved {len(collection_data)} customers from '{collection_name}' collection:\n" + '\n'.join(customer_list)

    elif collection_name == 'products':

        product_list = []

        for product in collection_data:

            product_info = f"Product: {product['product_name']} ({product['category']}) - Price: ${product['price']}"

            yearly_info = []

            for year_data in product['yearly_sales']:

                yearly_info.append(f"{year_data['year']}: {year_data['units_sold']} units, ${year_data['revenue']}")

            product_info += f"\n  Sales: {', '.join(yearly_info)}"

            product_list.append(product_info)

        return f"Retrieved {len(collection_data)} products from '{collection_name}' collection:\n" + '\n'.join(product_list)

    else:

        return f"Retrieved {len(collection_data)} documents from '{collection_name}' collection in database '{mongoUri}'."
@mcp.tool()
@safe_tool
def get_secret(secret_name: str, mask_sensitive: bool, confirm_unmask: str) -> str:

    '''```python
    """
    Retrieves a specific secret with options to mask or unmask sensitive fields.

    By default, sensitive fields such as passwords and usernames are masked.
    To unmask these fields, a confirmation is required.

    Args:
        secret_name (str): The name of the secret to retrieve. If None, a list of available secrets is returned.
        mask_sensitive (bool): If True, masks sensitive fields in the secret data.
        confirm_unmask (str): A confirmation string required to unmask sensitive fields.
            Must be 'yes, I understand' to proceed with unmasking.

    Returns:
        str: A message indicating the result of the retrieval. This includes the secret data with masked or unmasked
        sensitive fields, or an error message if the operation fails.
    """
```'''

    mock_secrets_db = {'rds_sqlserver_credentials': {'username': 'app_user', 'password': 'P@ssw0rd!2024', 'host': 'rds-sqlserver-instance.abc123xyz.us-east-1.rds.amazonaws.com', 'port': 1433, 'database': 'production_db'}, 'pyodbc_connection_string': {'connection_string': 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=rds-sqlserver-instance.abc123xyz.us-east-1.rds.amazonaws.com,1433;DATABASE=production_db;UID=app_user;PWD=P@ssw0rd!2024;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'}}

    if secret_name is not None and (not isinstance(secret_name, str)):

        return "Error: 'secret_name' must be a string if provided."

    if not isinstance(mask_sensitive, bool):

        return "Error: 'mask_sensitive' must be a boolean."

    if not isinstance(confirm_unmask, str):

        return "Error: 'confirm_unmask' must be a string."

    if secret_name is None:

        return f"Available secrets: {', '.join(mock_secrets_db.keys())}"

    if secret_name not in mock_secrets_db:

        return f"Error: Secret '{secret_name}' not found."

    secret_data = mock_secrets_db[secret_name].copy()

    def mask_value(value):

        if isinstance(value, str):

            if len(value) <= 4:

                return '*' * len(value)

            return value[0:2] + '*' * (len(value) - 4) + value[-2:]

        return value

    if mask_sensitive:

        for key in secret_data:

            if any((sens in key.lower() for sens in ['password', 'pwd', 'username', 'connection_string'])):

                secret_data[key] = mask_value(secret_data[key])

    elif confirm_unmask.strip().lower() != 'yes, i understand':

        return "Error: Unmasking sensitive data requires confirmation. Please provide 'yes, I understand' as confirm_unmask."

    return f"Retrieved secret '{secret_name}': {secret_data}"
@mcp.tool()
@safe_tool
def get_time(timezone: List[str]) -> str:

    '''```python
"""
Retrieve current time information for specified timezones.
This function returns the current time for each timezone provided in the input list.
The time information is formatted as a string for each requested timezone.
Args:
    timezone (List[str]): A list of timezone strings in the 'Continent/City' format
        (e.g., ['America/New_York', 'Europe/London']). Each string must represent a valid
        timezone.
Returns:
    str: A string containing the current time information for each timezone,
    separated by double newlines. Each entry is formatted as:
    "The current time in {timezone} is {current_time}."
"""
```'''

    mock_timezone_to_time = {'America/New_York': {'time': '18:00'}, 'America/Los_Angeles': {'time': '15:00'}, 'Europe/London': {'time': '23:00'}, 'Asia/Tokyo': {'time': '08:00'}, 'Europe/Paris': {'time': '00:00'}, 'Europe/Berlin': {'time': '00:00'}, 'Australia/Sydney': {'time': '09:00'}, 'America/Chicago': {'time': '17:00'}}

    if not timezone or not isinstance(timezone, list):

        return "Error: 'timezone' parameter must be a non-empty list of strings."

    invalid_timezones = []

    for tz in timezone:

        if not isinstance(tz, str) or '/' not in tz:

            invalid_timezones.append(tz)

    if invalid_timezones:

        return f"Error: Invalid timezone formats found: {', '.join(invalid_timezones)}. Timezones must be in 'Region/City' format."

    results = []

    for tz in timezone:

        timezone_info = mock_timezone_to_time.get(tz, {'time': '00:00'})

        example_time = timezone_info['time']

        mock_current_time = f'{example_time}:00'

        result = f'The current time in {tz} is {mock_current_time}.'

        results.append(result)

    return '\n\n'.join(results)
@mcp.tool()
@safe_tool
def get_ip_details(ip_address: List[str]) -> str:

    '''```python
"""
Retrieve detailed information about IP addresses, including geolocation data.
This function accepts a list of IP addresses and returns detailed information
for each, including the country, region, city, and timezone. It validates the
format of each IP address and provides an error message for any invalid entries.
Args:
    ip_address (List[str]): A non-empty list of IP address strings to be
    processed. Each IP address should be a valid IPv4 or IPv6 format.
Returns:
    str: A formatted string containing geolocation details for each valid IP
    address. If an IP address is invalid or no data is found, an error message
    is returned.
"""
```'''

    mock_ip_db = {'203.0.113.25': {'ip': '203.0.113.25', 'country': 'United States', 'region': 'New York', 'city': 'New York City', 'timezone': 'America/New_York'}, '198.51.100.42': {'ip': '198.51.100.42', 'country': 'United Kingdom', 'region': 'England', 'city': 'London', 'timezone': 'Europe/London'}, '192.0.2.88': {'ip': '192.0.2.88', 'country': 'Japan', 'region': 'Tokyo', 'city': 'Tokyo', 'timezone': 'Asia/Tokyo'}}

    import re

    def is_valid_ip(ip):

        ipv4_pattern = '^\\d{1,3}(\\.\\d{1,3}){3}$'

        ipv6_pattern = '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'

        return bool(re.match(ipv4_pattern, ip)) or bool(re.match(ipv6_pattern, ip))

    if not ip_address or not isinstance(ip_address, list):

        return "Error: 'ip_address' parameter must be a non-empty list of strings."

    invalid_ips = []

    for ip in ip_address:

        if not isinstance(ip, str) or not is_valid_ip(ip):

            invalid_ips.append(ip)

    if invalid_ips:

        return f"Error: Invalid IP addresses found: {', '.join(invalid_ips)}"

    results = []

    for ip in ip_address:

        if ip in mock_ip_db:

            ip_info = mock_ip_db[ip]

            result = f"IP Address: {ip_info['ip']}\nCountry: {ip_info['country']}\nRegion: {ip_info['region']}\nCity: {ip_info['city']}\nTimezone: {ip_info['timezone']}"

            results.append(result)

        else:

            results.append(f"No geolocation data found for IP address '{ip}'.")

    return '\n\n'.join(results)
@mcp.tool()
@safe_tool
def nmap_scan(host: str, ports: str, arguments: str) -> str:

    '''```python
    """
    Performs a network scan on the specified host to detect open ports and services.

    This function utilizes Nmap to conduct a network scan on the given host, identifying
    open ports and their corresponding services. The scan can be customized using specific
    arguments to tailor the detection process.

    Args:
        host (str): The target host for the network scan. Must be a non-empty string.
        ports (str): A comma-separated list of ports to scan. Must be a non-empty string.
        arguments (str): Additional Nmap command-line arguments for customizing the scan.
            Must be a non-empty string.

    Returns:
        str: A formatted string containing the results of the network scan, including
        information about open ports, detected services, and service versions.
    """
```'''

    mock_scan_results = {('192.168.1.10', '80,443', '-sV'): 'Starting Nmap 7.93 ( https://nmap.org ) at 2024-06-15 12:00 UTC\nNmap scan report for 192.168.1.10\nHost is up (0.0021s latency).\n\nPORT    STATE SERVICE  VERSION\n80/tcp  open  http     Apache httpd 2.4.41 ((Ubuntu))\n443/tcp open  https    OpenSSL 1.1.1f TLSv1.3\nService Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel\n\nNmap done: 1 IP address (1 host up) scanned in 1.35 seconds', ('adserver.example.com', '80,443,3306', '-sV'): 'Starting Nmap 7.93 ( https://nmap.org ) at 2024-06-15 12:01 UTC\nNmap scan report for adserver.example.com (203.0.113.25)\nHost is up (0.045s latency).\n\nPORT     STATE SERVICE    VERSION\n80/tcp   open  http       nginx 1.18.0\n443/tcp  open  https      nginx 1.18.0\n3306/tcp open  mysql      MySQL 5.7.33\nService Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel\n\nNmap done: 1 IP address (1 host up) scanned in 2.05 seconds', ('10.0.0.5', '22,8080', '-sV --script vuln'): 'Starting Nmap 7.93 ( https://nmap.org ) at 2024-06-15 12:02 UTC\nNmap scan report for 10.0.0.5\nHost is up (0.0018s latency).\n\nPORT     STATE SERVICE  VERSION\n22/tcp   open  ssh      OpenSSH 7.4 (protocol 2.0)\n8080/tcp open  http-proxy Apache Tomcat/Coyote JSP engine 1.1\n| http-vuln-cve2006-3392: \n|   VULNERABLE:\n|   Apache Tomcat JSP source code disclosure\n|     State: VULNERABLE\n|_    IDs:  CVE:CVE-2006-3392\n\nService Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel\n\nNmap done: 1 IP address (1 host up) scanned in 4.12 seconds'}

    if not isinstance(host, str) or not host.strip():

        raise ValueError('Invalid host: must be a non-empty string')

    if not isinstance(ports, str) or not ports.strip():

        raise ValueError('Invalid ports: must be a non-empty string')

    if not isinstance(arguments, str) or not arguments.strip():

        raise ValueError('Invalid arguments: must be a non-empty string')

    key = (host.strip(), ports.strip(), arguments.strip())

    if key in mock_scan_results:

        return mock_scan_results[key]

    else:

        return f'Starting Nmap 7.93 ( https://nmap.org ) at 2024-06-15 12:05 UTC\nNmap scan report for {host.strip()}\nHost is up (0.050s latency).\n\nPORT(S)   STATE  SERVICE  VERSION\n{ports.strip()}   open   unknown  Unknown service\nService Info: OS: Unknown\n\nNmap done: 1 IP address (1 host up) scanned in 1.00 seconds'
@mcp.tool()
@safe_tool
def make_api_request(apiName: str, url: str, endpoint: str) -> str:

    '''```python
    """
    Sends an HTTP GET request to a specified public or internal API using either an API name with an endpoint or a full URL.
    The function applies authentication if available and returns structured results including status, headers, response body,
    and pagination hints. It is typically used after discovering an API schema to fetch real data for analysis or visualization.

    Args:
        apiName (str): The identifier for the API. Use lowercase with underscores for spaces.
                       Example: "City Earthquake Data API" becomes "city_earthquake_data_api".
                       Supported APIs: "earthquake_api", "ecommerce_api".
        url (str): The full URL of the API endpoint (e.g., "https://api.earthquake.example.com").
        endpoint (str): The specific endpoint path (e.g., "/earthquakes").

    Returns:
        str: A message indicating the success or failure of the API connection attempt.

    Example:
        make_api_request("city_earthquake_data_api", "https://api.earthquake.example.com", "/earthquakes")
    """
```'''

    mock_api_data = {'city_earthquake_data_api': {'base_url': 'https://api.earthquake.example.com', 'endpoints': {'/earthquakes': {'description': 'Returns recent earthquakes in a given city within the last 30 days', 'mock_response': {'status': 200, 'headers': {'Content-Type': 'application/json', 'X-RateLimit-Remaining': '98'}, 'body': {'city': 'San Francisco', 'timeframe_days': 30, 'earthquakes': [{'id': 'eq001', 'date': '2024-05-20T14:32:00Z', 'magnitude': 4.2, 'depth_km': 8.1, 'location': {'lat': 37.7749, 'lon': -122.4194}}, {'id': 'eq002', 'date': '2024-05-25T08:12:00Z', 'magnitude': 3.8, 'depth_km': 5.4, 'location': {'lat': 37.8044, 'lon': -122.2711}}]}, 'pagination': {'next': None, 'previous': None}}}}}, 'ecommerce_api': {'base_url': 'https://api.ecommerce.example.com', 'endpoints': {'/products': {'description': 'Returns a list of products available in the e-commerce store', 'mock_response': {'status': 200, 'headers': {'Content-Type': 'application/json', 'X-RateLimit-Remaining': '495'}, 'body': {'products': [{'id': 'p1001', 'name': 'Wireless Headphones', 'price_usd': 99.99, 'in_stock': True}, {'id': 'p1002', 'name': 'Gaming Laptop', 'price_usd': 1299.0, 'in_stock': False}, {'id': 'p1003', 'name': 'Smartphone', 'price_usd': 799.5, 'in_stock': True}]}, 'pagination': {'next': 'https://api.ecommerce.example.com/products?page=2', 'previous': None}}}, '/orders': {'description': 'Returns recent customer orders', 'mock_response': {'status': 200, 'headers': {'Content-Type': 'application/json'}, 'body': {'orders': [{'order_id': 'o9001', 'customer': 'John Doe', 'total_usd': 159.98, 'status': 'shipped'}, {'order_id': 'o9002', 'customer': 'Jane Smith', 'total_usd': 799.5, 'status': 'processing'}]}, 'pagination': {'next': None, 'previous': None}}}}}, 'image_object_detection_api': {'base_url': 'https://api.example.com', 'endpoints': {'v1/object-detection': {'description': 'Detects objects in an image from a provided image URL and returns an updated image with bounding boxes around detected objects. Optionally returns JSON metadata of detections.', 'mock_response': {'status': 200, 'headers': {'Content-Type': 'application/json'}, 'body': {'detections': [{'object': 'cat', 'confidence': 0.98, 'bounding_box': {'x_min': 34, 'y_min': 45, 'x_max': 200, 'y_max': 300}}, {'object': 'dog', 'confidence': 0.95, 'bounding_box': {'x_min': 220, 'y_min': 80, 'x_max': 400, 'y_max': 350}}]}, 'pagination': {'next': None, 'previous': None}}}}}}

    if not apiName or not isinstance(apiName, str):

        return "Error: 'apiName' must be a non-empty string."

    if not url or not isinstance(url, str):

        return "Error: 'url' must be a non-empty string."

    if not endpoint or not isinstance(endpoint, str):

        return "Error: 'endpoint' must be a non-empty string."

    api_info = mock_api_data.get(apiName.lower())

    if not api_info:

        return f"Error: API '{apiName}' not found in mock database."

    endpoint_info = api_info['endpoints'].get(endpoint)

    if not endpoint_info:

        return f"Error: Endpoint '{endpoint}' not available for API '{apiName}'."

    expected_url = api_info['base_url'] + endpoint

    if url != expected_url:

        return f'Error: Provided URL does not match the expected endpoint URL: {expected_url}'

    if apiName.lower() == 'ecommerce_api':

        return f"Successfully connected to API '{apiName}' at endpoint '{endpoint}'. Database ecommerce_sales is connected and retrieved."

    return f"Successfully connected to API '{apiName}' at endpoint '{endpoint}'."
@mcp.tool()
@safe_tool
def request_api_schema(ApiName: Union[str, List[str]]) -> str:

    '''```python
    """
    Retrieves the API request schema(s) for specified API name(s).

    This function accepts either a single API name as a string or a list of API names.
    It returns the corresponding request schema(s) for the provided API name(s).
    If a single API name is provided, a single schema is returned. If a list of API
    names is provided, multiple schemas are returned.

    Args:
        ApiName (Union[str, List[str]]): A single API name as a string or a list of
            API names. Each name should be a non-empty string.
            Each word in the API name should be capitalized.
            For Example, 'Image Object Detection API'

    Returns:
        str: A formatted string containing the API schema(s). If no schema is found
        for a given API name, an error message is included. If multiple API names
        are provided, the result includes all found schemas and any warnings for
        missing schemas.
    """
```'''

    mock_api_schemas = {

        'Image Object Detection API': {

            'description': 'Detects objects in an image from a provided image URL and returns an updated image with bounding boxes around detected objects. Optionally returns JSON metadata of detections.',

            'endpoint': 'POST https://api.example.com/v1/object-detection',

            'request_schema': {

                'image_url': 'string (URL to the image to process)',

                'return_json': 'boolean (optional, if true returns detection metadata)'

            }

        },

        'City Earthquake Data API': {

            'description': 'Retrieves all earthquakes in a given city within the last 30 days.',

            'endpoint': 'GET https://api.example.com/v1/earthquakes',

            'request_schema': {

                'city': 'string (name of the city)',

                'days': 'integer (optional, default 30)'

            }

        },

        'Microsoft Translator Text API': {

            'description': 'Provides translation services and lists supported languages.',

            'endpoint': 'GET https://api.cognitive.microsofttranslator.com/languages',

            'request_schema': {

                'scope': "string (optional, e.g., 'translation', 'transliteration', 'dictionary')"

            }

        },

        'Simple & Elegant Translation Service API': {

            'description': 'Lightweight translation API supporting multiple languages.',

            'endpoint': 'GET https://api.simpletranslate.com/v1/languages',

            'request_schema': {

                'format': "string (optional, e.g., 'json', 'xml')"

            }

        },

        'LanguageTool API': {

            'description': 'Grammar, style, and spell checking for multiple languages.',

            'endpoint': 'GET https://api.languagetool.org/v2/languages',

            'request_schema': {

                'api_key': 'string (optional, if required for premium usage)'

            }

        },

        'Vision Detect 3D API': {

            'description': 'Performs high-accuracy 3D object detection on input data (image sets, depth maps, or point clouds). Returns detected objects with 3D bounding boxes and annotated previews.',

            'endpoint': 'POST https://api.example.com/v1/vision-detect-3d',

            'request_schema': {

                'input_type': "string (required, one of: 'image_set', 'depth_map', 'point_cloud')",

                'data_url': 'string (URL pointing to the 3D data or file to process)',

                'confidence_threshold': 'float (optional, default 0.5, threshold for valid detections)',

                'return_3d_preview': 'boolean (optional, if true returns a rendered 3D visualization with highlighted bounding volumes)'

            }

        },

        'OCR Text Extract API': {

            'description': 'Extracts readable text from image/URL using OCR; returns plain text and layout hints.',

            'endpoint': 'POST https://api.example.com/v1/ocr-extract',

            'request_schema': {

                'image_url': 'string (URL to the image to extract text from)',

                'language_hint': 'string (optional, ISO code for expected text language)'

            }

        },

        'USGS Earthquake Feed API (Mock)': {

            'description': 'Query recent earthquakes by region, magnitude, and time window.',

            'endpoint': 'GET https://api.example.com/v1/usgs-quakes',

            'request_schema': {

                'region': 'string (optional, geographic region filter)',

                'min_magnitude': 'float (optional, minimum magnitude to filter)',

                'start_date': 'string (optional, start date in YYYY-MM-DD)',

                'end_date': 'string (optional, end date in YYYY-MM-DD)'

            }

        },

        'Grammarify Proofread API (Mock)': {

            'description': 'Proofreading and grammar correction for multilingual text.',

            'endpoint': 'POST https://api.example.com/v1/grammarify',

            'request_schema': {

                'text': 'string (the text content to proofread)',

                'language': "string (ISO language code, e.g., 'en', 'fr')",

                'return_suggestions': 'boolean (optional, default true, include correction suggestions)'

            }

        },

        'Ecommerce API': {

            'description': 'API for managing e-commerce operations including products, orders, and customers.',

            'endpoint': 'https://api.ecommerce.com/v1/',

            'request_schema': {

                'product_id': 'string (ID of the product)',

                'order_id': 'string (ID of the order)',

                'customer_id': 'string (ID of the customer)',

                'action': "string (action to perform, e.g., 'create', 'update', 'delete')"

            }

        }

    }

    if isinstance(ApiName, str):

        if not ApiName.strip():

            return "Error: 'ApiName' must be a non-empty string."

        api_names = [ApiName.strip()]

        is_single = True

    elif isinstance(ApiName, list):

        if not ApiName:

            return "Error: 'ApiName' list cannot be empty."

        api_names = [name.strip() for name in ApiName if isinstance(name, str) and name.strip()]

        if not api_names:

            return "Error: 'ApiName' list must contain non-empty strings."

        is_single = False

    else:

        return "Error: 'ApiName' must be either a string or a list of strings."

    results = []

    errors = []

    for api_name in api_names:

        schema = mock_api_schemas.get(api_name)

        if not schema:

            errors.append(f"No schema found for '{api_name}'")

        else:

            schema_info = f"API Name: {api_name}\nDescription: {schema['description']}\nEndpoint: {schema['endpoint']}\nRequest Schema: {schema['request_schema']}"

            results.append(schema_info)

    if not results:

        return f"Error: {', '.join(errors)}"

    if is_single:

        if errors:

            return f"Warning: {', '.join(errors)}\n\n{results[0]}"

        return results[0]

    else:

        output_lines = [f'Found {len(results)} API schema(s):']

        for (i, result) in enumerate(results, 1):

            output_lines.append(f'\n--- Schema {i} ---')

            output_lines.append(result)

        if errors:

            output_lines.append(f"\nWarnings: {', '.join(errors)}")

        return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def searchApis(keyword: str) -> str:

    '''```python
    """
    Searches for APIs based on a given label keyword, with a case-insensitive approach.

    The search prioritizes:
      1) Exact label matches
      2) Partial label matches (as substrings)
      3) Partial API-name matches (as substrings)

    The function returns a formatted string with the results:
      - For a single label match: "<label>: api1, api2, ..."
      - For multiple label matches: Each label and its APIs on a new line in the format "<label>: api1, api2, ..."
      - If no matches are found: "No APIs found for keyword '<keyword>'."

    Args:
        keyword (str): The label keyword to search for. Must be a non-empty string, should be one of [object detection, image recognition, earthquake, translation, language correction, pdf rendering, document rendering, content moderation, profanity detection].

    Returns:
        str: A formatted string of matched APIs or an error message if no matches are found.
    """
```'''

    if not isinstance(keyword, str) or not keyword.strip():

        return "Error: 'keyword' must be a non-empty string."

    q = keyword.strip().lower()

    mock_api_db = {'object detection': ['Image Object Detection API'], 'image recognition': ['Image Object Detection API', 'Vision Detect Pro API', 'OCR Text Extract API'], 'earthquake': ['City Earthquake Data API', 'USGS Earthquake Feed API (Mock)'], 'translation': ['Microsoft Translator Text API', 'Simple & Elegant Translation Service API'], 'language correction': ['LanguageTool API', 'Grammarify Proofread API (Mock)'], 'pdf rendering': ['RenderFlow PDF API', 'PDF Render Job API', 'PDF Render Status API'], 'document rendering': ['RenderFlow PDF API', 'PDF Render Job API', 'PDF Render Status API'], 'profanity detection': ['Profanity Filter API', 'Content Moderation Check API']}

    api_to_labels = {}

    for (label, apis) in mock_api_db.items():

        for api in apis:

            api_to_labels.setdefault(api, set()).add(label)

    exact_hits = []

    for label in mock_api_db.keys():

        if q == label.lower():

            exact_hits.append(label)

    if exact_hits:

        ordered = [lbl for lbl in mock_api_db.keys() if lbl in exact_hits]

        lines = [f"{lbl}: {', '.join(mock_api_db[lbl])}" for lbl in ordered]

        return '\n'.join(lines)

    partial_label_hits = []

    for label in mock_api_db.keys():

        if q in label.lower():

            partial_label_hits.append(label)

    if partial_label_hits:

        ordered = [lbl for lbl in mock_api_db.keys() if lbl in partial_label_hits]

        lines = [f"{lbl}: {', '.join(mock_api_db[lbl])}" for lbl in ordered]

        return '\n'.join(lines)

    candidate_labels = []

    for api_name in api_to_labels.keys():

        if q in api_name.lower():

            candidate_labels.extend(list(api_to_labels[api_name]))

    seen = set()

    ordered_candidates = []

    for lbl in mock_api_db.keys():

        if lbl in candidate_labels and lbl not in seen:

            seen.add(lbl)

            ordered_candidates.append(lbl)

    if ordered_candidates:

        lines = [f"{lbl}: {', '.join(mock_api_db[lbl])}" for lbl in ordered_candidates]

        return '\n'.join(lines)

    return f"No APIs found for keyword '{keyword.strip()}'."
@mcp.tool()
@safe_tool
def vector_search(query: str, limit: int) -> str:

    '''```python
    """
    Perform semantic search across stored documents.

    This function executes a semantic search based on a given query string,
    retrieving and ranking stored documents according to their relevance.
    The relevance is determined using cosine similarity between the query
    embedding and document embeddings. The top results are returned up to
    the specified limit.

    Args:
        query (str): A non-empty string representing the search query.
        limit (int): A positive integer specifying the maximum number of
            top results to return.

    Returns:
        str: A formatted string containing the top matching documents'
        metadata, including model details, learning rate, l1 ratio,
        convergence speed, final error, and notes, along with their
        similarity scores. If no similar documents are found, returns
        'No similar experiments found.'
    """
```'''

    mock_vector_db = [{'id': 'exp001', 'embedding': [0.12, 0.56, 0.33, 0.89], 'metadata': {'model': 'SGDRegressor', 'regularization': 'ElasticNet', 'learning_rate': 0.01, 'l1_ratio': 0.2, 'convergence_speed': 'fast', 'final_error': 0.045, 'notes': 'Performed well on small dataset of US city housing prices.'}}, {'id': 'exp002', 'embedding': [0.14, 0.54, 0.31, 0.87], 'metadata': {'model': 'SGDRegressor', 'regularization': 'ElasticNet', 'learning_rate': 0.005, 'l1_ratio': 0.5, 'convergence_speed': 'medium', 'final_error': 0.052, 'notes': 'Balanced l1/l2 penalty improved stability but slower convergence.'}}, {'id': 'exp003', 'embedding': [0.85, 0.12, 0.65, 0.24], 'metadata': {'model': 'SGDRegressor', 'regularization': 'ElasticNet', 'learning_rate': 0.02, 'l1_ratio': 0.8, 'convergence_speed': 'very fast', 'final_error': 0.06, 'notes': 'High l1_ratio led to sparse weights, but slightly higher error.'}}, {'id': 'exp004', 'embedding': [0.11, 0.53, 0.34, 0.88], 'metadata': {'model': 'SGDRegressor', 'regularization': 'ElasticNet', 'learning_rate': 0.01, 'l1_ratio': 0.3, 'convergence_speed': 'fast', 'final_error': 0.046, 'notes': 'Similar to exp001 with marginally different l1_ratio.'}}]

    if not isinstance(query, str) or not query.strip():

        raise ValueError("Parameter 'query' must be a non-empty string.")

    if not isinstance(limit, int) or limit <= 0:

        raise ValueError("Parameter 'limit' must be a positive integer.")

    import random

    random.seed(abs(hash(query)) % 10 ** 6)

    query_embedding = [random.random() for _ in range(4)]

    def cosine_similarity(vec1, vec2):

        import math

        dot_prod = sum((a * b for (a, b) in zip(vec1, vec2)))

        norm1 = math.sqrt(sum((a * a for a in vec1)))

        norm2 = math.sqrt(sum((b * b for b in vec2)))

        if norm1 == 0 or norm2 == 0:

            return 0

        return dot_prod / (norm1 * norm2)

    scored_results = []

    for record in mock_vector_db:

        score = cosine_similarity(query_embedding, record['embedding'])

        scored_results.append((score, record))

    scored_results.sort(key=lambda x: x[0], reverse=True)

    top_results = scored_results[:limit]

    output_lines = []

    for (score, rec) in top_results:

        meta = rec['metadata']

        output_lines.append(f"ID: {rec['id']}, Model: {meta['model']}, LR: {meta['learning_rate']}, l1_ratio: {meta['l1_ratio']}, Convergence: {meta['convergence_speed']}, Final Error: {meta['final_error']}, Notes: {meta['notes']} (Similarity: {score:.3f})")

    return '\n'.join(output_lines) if output_lines else 'No similar experiments found.'
@mcp.tool()
@safe_tool
def wolfram_query(query: str, format: str, location: str) -> str:

    '''```python
    """
    Queries Wolfram Alpha for a wide range of information including computational, mathematical, scientific,
    geographic, and factual data.

    This function interfaces with Wolfram Alpha's computational knowledge engine to facilitate research and analysis.
    It supports natural language queries and can provide statistical data, research findings, and analytical
    information across various domains such as technology adoption, industry statistics, and market research.

    Args:
        query (str): The query string or question to be sent to Wolfram Alpha, e.g.,
            "Statistics on adoption of virtual reality technology in architecture".
        format (str): The preferred format for the results, such as "json", "text", or "table".
        location (str): The geographic scope for the query, e.g., "globalchch", "US", or "Europe".

    Returns:
        str: A JSON-formatted string containing research data, statistics, and analytical results
        from Wolfram Alpha's knowledge base. The response may include information on technology
        adoption, industry trends, efficiency metrics, cost analysis, and market impact data.

    Example:
        Query: "Statistics on adoption of virtual reality technology in architecture and global construction industry"
        Returns: A JSON string with VR adoption rates, efficiency improvements, cost reductions,
                 and customer experience metrics in the construction industry.
    """
```'''

    result = f'模拟Query Wolfram Alpha for computational, mathematical, scientific, geographic, and factual information. Supports natural language questions and returns the message of data successfully fetched or not. Useful for advanced calculations, model validation, scientific context, and real-world data lookup. It can localize results with unit or currency preferences.的结果'

    return result
@mcp.tool()
@safe_tool
def WebSearchConfig(name: str, description: str, search_engine: str, max_results: str, extract_content: str) -> str:

    '''```python
    """
    Configures the web search tool with specified parameters.

    This function sets up a web search configuration using the provided
    parameters such as the name, description, search engine, maximum number
    of results, and content extraction preference. It validates the input
    parameters and returns a confirmation message upon successful configuration.

    Args:
        name (str): The name of the web search configuration. Must be a non-empty string, must be one of [Default Web Search, Nearby Restaurants Search].
        description (str): A brief description of the web search configuration. Must be a non-empty string.
        search_engine (str): The search engine to be used (e.g., 'Google'). Must be a non-empty string.
        max_results (str): The maximum number of search results to return. Must be a non-empty string containing digits only.
        extract_content (str): A flag indicating whether to extract content ('true' or 'false'). Must be one of these strings.

    Returns:
        str: A message confirming the successful creation of the web search configuration.
    """
```'''

    mock_config_db = {'Nearby Restaurants Search': {'name': 'Nearby Restaurants Search', 'description': 'Search for restaurants near the current location based on user preferences.', 'search_engine': 'Google', 'max_results': '20', 'extract_content': 'true', 'url': 'https://maps.google.com/search/restaurants'}, 'Default Web Search': {'name': 'Default Web Search', 'description': 'General web search configuration for various purposes.', 'search_engine': 'Google', 'max_results': '10', 'extract_content': 'false', 'url': 'https://google.com/defaultsearch'}}

    if not isinstance(name, str) or not name.strip():

        raise ValueError("Parameter 'name' must be a non-empty string.")

    if not isinstance(description, str) or not description.strip():

        raise ValueError("Parameter 'description' must be a non-empty string.")

    if not isinstance(search_engine, str) or not search_engine.strip():

        raise ValueError("Parameter 'search_engine' must be a non-empty string.")

    if not isinstance(max_results, str) or not max_results.strip() or (not max_results.isdigit()):

        raise ValueError("Parameter 'max_results' must be a non-empty string containing digits only.")

    if not isinstance(extract_content, str) or extract_content.lower() not in ['true', 'false']:

        raise ValueError("Parameter 'extract_content' must be a string 'true' or 'false'.")

    config_key = name.strip()

    mock_config_db[config_key] = {'name': name.strip(), 'description': description.strip(), 'search_engine': search_engine.strip(), 'max_results': max_results.strip(), 'extract_content': extract_content.strip().lower(), 'url': f'https://maps.google.com/search/restaurants' if 'restaurant' in description.lower() or 'restaurants' in description.lower() else 'https://google.com/defaultsearch'}

    if 'restaurant' in description.lower() or 'restaurants' in description.lower():

        response_msg = f"Web search configuration '{name}' has been set up to use {search_engine} engine, returning up to {max_results} results, with content extraction set to {extract_content}, the deployed url is {mock_config_db[config_key]['url']}. This configuration is optimized for finding nearby restaurants."

    else:

        response_msg = f"Web search configuration '{name}' successfully created with {search_engine} engine and max {max_results} results (extract_content={extract_content}) and the deployed url is {mock_config_db[config_key]['url']}."

    return response_msg
@mcp.tool()
@safe_tool
def security_guidance(query: str) -> str:

    '''```python
    """
    Provides actionable, non-sensitive security recommendations for applications
    and data systems based on a given query. The function returns best-practice
    checklists, minimal configuration or code snippets (e.g., MySQL TLS,
    least-privilege GRANTs, parameterized queries), data protection advice
    (e.g., PII handling, encryption at rest/in transit), access control/RBAC
    patterns, logging and monitoring strategies, and compliance pointers
    (e.g., GDPR, FERPA). It ensures no secrets are requested or returned,
    using placeholders in examples.

    Args:
        query (str): A non-empty string representing the security-related
        question or topic for which guidance is sought.

    Returns:
        str: A string containing security recommendations and best practices
        tailored to the query, formatted as checklists, code snippets, or
        advisory notes.
    """
```'''

    if not isinstance(query, str) or not query.strip():

        raise ValueError("Parameter 'query' must be a non-empty string.")

    mock_guidance_db = {'protect data from cyberattacks': 'Security Best Practices for Protecting Data from Cyberattacks:\n1. Implement strong authentication (MFA) for all user accounts.\n2. Enforce least privilege access controls and role-based access control (RBAC).\n3. Keep systems, libraries, and dependencies up-to-date with security patches.\n4. Use encryption at rest (AES-256) and in transit (TLS 1.2+).\n5. Regularly back up data and store backups in a secure, isolated environment.\n6. Monitor logs for suspicious activity and set up automated alerts.\n7. Perform regular security audits and penetration testing.\n8. Train employees on security awareness and phishing prevention.', 'secure mysql connection': "Checklist for Securing a MySQL Connection:\n1. Enable TLS/SSL in MySQL:\n   ```\n   # In my.cnf\n   [mysqld]\n   require_secure_transport = ON\n   ssl_cert = /path/to/server-cert.pem\n   ssl_key = /path/to/server-key.pem\n   ssl_ca = /path/to/ca-cert.pem\n   ```\n2. Create a least-privilege user:\n   ```\n   CREATE USER 'app_user'@'%' IDENTIFIED BY 'PLACEHOLDER_PASSWORD';\n   GRANT SELECT, INSERT, UPDATE, DELETE ON moviedb.* TO 'app_user'@'%';\n   FLUSH PRIVILEGES;\n   ```\n3. Store credentials securely (e.g., environment variables, secrets manager).\n4. Use parameterized queries to prevent SQL injection.\n5. Regularly rotate database credentials.\n6. Restrict network access to trusted IPs only.\n7. Enable query logging and monitor for anomalies.", 'online learning platform privacy': 'Security and Privacy Guidance for an Online Learning Platform:\n1. Collect only the minimum necessary personal data from students.\n2. Encrypt sensitive data at rest using AES-256.\n3. Use HTTPS/TLS for all data in transit.\n4. Implement RBAC: separate roles for students, teachers, and admins with appropriate permissions.\n5. Store credentials in a secure secrets manager — never in source code.\n6. Comply with relevant privacy regulations (e.g., FERPA, GDPR).\n7. Log all access to student records and review logs regularly.\n8. Implement account lockout after repeated failed login attempts.\n9. Provide users with clear privacy policies and obtain consent where required.'}

    normalized_query = query.strip().lower()

    if 'cyberattack' in normalized_query or 'protect data' in normalized_query:

        return mock_guidance_db['protect data from cyberattacks']

    elif 'mysql' in normalized_query or 'secure connection' in normalized_query:

        return mock_guidance_db['secure mysql connection']

    elif 'online learning' in normalized_query or 'student information' in normalized_query or 'privacy' in normalized_query:

        return mock_guidance_db['online learning platform privacy']

    else:

        return 'General Application Security Guidelines:\n1. Apply the principle of least privilege to all systems and services.\n2. Keep all software dependencies updated and patched.\n3. Enforce strong authentication and use MFA where possible.\n4. Encrypt sensitive data both at rest and in transit.\n5. Validate and sanitize all user inputs to prevent injection attacks.\n6. Monitor system logs and set up alerts for suspicious activity.\n7. Back up data regularly and test restoration procedures.\n8. Stay informed about relevant compliance requirements.'
@mcp.tool()
@safe_tool
def CountDown_StartAndEndDate(Ele: str, StartDate: str, EndDate: str, EndFunc: str=None) -> str:

    '''```python
"""
Creates a customizable countdown timer between a defined start and end date.
This function initializes a countdown timer that tracks the time remaining between a specified start date and end date. It updates a target element with the remaining time and can optionally trigger a callback function when the countdown ends. This is useful for creating timers for vocabulary sessions, timed quizzes, or any time-limited activities.
Args:
    Ele (str): The identifier of the target element where the countdown will be displayed. Must be a non-empty string representing the DOM element or component.
    StartDate (str): The start date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). The countdown begins when this time is reached.
    EndDate (str): The end date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). The countdown ends when this time is reached. Must be later than StartDate.
    EndFunc (str, optional): A callback function to execute when the countdown ends. Can be None if no callback is needed.
Returns:
    str: A status message indicating the result of the countdown creation. Possible messages include:
         - "Countdown scheduled to start at {StartDate}" if the current time is before the start time.
         - "Countdown running: {seconds} seconds remaining" if the countdown is currently active.
         - "Countdown already ended." if the end time has passed.
         - Error messages for invalid parameters or date formats.
Raises:
    ValueError: If Ele is not a valid string, if the dates are in an invalid format, or if EndDate is not later than StartDate.
"""
```'''

    mock_countdowns_db = {}

    if not Ele or not isinstance(Ele, str):

        return 'Error: Invalid Ele parameter. Must be a non-empty string representing target element.'

    if not StartDate or not isinstance(StartDate, str):

        return "Error: Invalid StartDate parameter. Must be a date string in format 'YYYY-MM-DDTHH:MM:SS'."

    if not EndDate or not isinstance(EndDate, str):

        return "Error: Invalid EndDate parameter. Must be a date string in format 'YYYY-MM-DDTHH:MM:SS'."

    from datetime import datetime

    try:

        start_dt = datetime.fromisoformat(StartDate)

        end_dt = datetime.fromisoformat(EndDate)

    except ValueError:

        return 'Error: StartDate or EndDate is not in a valid ISO date format.'

    if end_dt <= start_dt:

        return 'Error: EndDate must be after StartDate.'

    now = datetime.now()

    if now < start_dt:

        countdown_status = 'Countdown scheduled to start at {}'.format(StartDate)

    elif start_dt <= now < end_dt:

        remaining = end_dt - now

        countdown_status = 'Countdown running: {} seconds remaining'.format(int(remaining.total_seconds()))

    else:

        countdown_status = 'Countdown already ended.'

        if EndFunc and EndFunc.strip():

            return f'Countdown ended. EndFunc callback "{EndFunc}" would be executed.'

        return 'Countdown not created because end time has already passed.'

    mock_countdowns_db[Ele] = {'start': StartDate, 'end': EndDate, 'status': countdown_status, 'callback_set': bool(EndFunc and EndFunc.strip())}

    if Ele.lower().startswith('vocab_timer'):

        return f"Vocabulary session countdown created for element '{Ele}'. {countdown_status}"

    return f"Countdown created for element '{Ele}'. {countdown_status}"
@mcp.tool()
@safe_tool
def create_comment(id: str, comment: str) -> str:

    '''```python
    """
    Create a new comment on an existing Linear issue.

    Args:
        id (str): The unique identifier of the Linear issue. Must be a non-empty string.
        comment (str): The text of the comment to be added. Must be a non-empty string.

    Returns:
        str: A confirmation message indicating successful creation of the comment for the specified issue.
    """
```'''

    if not isinstance(id, str) or not id.strip():

        raise ValueError("Invalid 'id': must be a non-empty string representing the issue ID.")

    if not isinstance(comment, str) or not comment.strip():

        raise ValueError("Invalid 'comment': must be a non-empty string containing the comment text.")

    return f"Comment created successfully for issue '{id}'."
@mcp.tool()
@safe_tool
def orchestrator_plan_task(topic: str, scope: str, schedule: str, constraints: List[str], dependencies: List[str]) -> str:

    '''```python
    """
    Generates a detailed task breakdown for orchestrating a data pipeline.

    This function creates a structured plan for executing a data pipeline
    based on the provided topic, scope, schedule, constraints, and dependencies.
    It returns a formatted string summarizing the task plan, including the
    breakdown of steps required to achieve the specified objectives.

    Args:
        topic (str): The specific topic or name of the data pipeline. Determines
            if a predefined plan is available.
        scope (str): A description of the scope of the task. Must be a non-empty string.
        schedule (str): The schedule in cron format for executing the task. Must be a non-empty string.
        constraints (List[str]): A list of constraints that must be considered during planning.
            Must be a non-empty list of strings.
        dependencies (List[str]): A list of dependencies that affect the task execution.
            Must be a non-empty list of strings.

    Returns:
        str: A formatted string summarizing the task plan, including the scope,
        schedule, constraints, dependencies, and a step-by-step breakdown of tasks.
    """
```'''

    if not scope or not isinstance(scope, str):

        raise ValueError("Parameter 'scope' is required and must be a non-empty string.")

    if not schedule or not isinstance(schedule, str):

        raise ValueError("Parameter 'schedule' is required and must be a non-empty string.")

    if not isinstance(constraints, list) or not constraints:

        raise ValueError("Parameter 'constraints' is required and must be a non-empty list.")

    if not isinstance(dependencies, list) or not dependencies:

        raise ValueError("Parameter 'dependencies' is required and must be a non-empty list.")

    mock_plans = {'Zoho & Pipedrive to BigQuery pipeline': [{'step': 1, 'task': 'Extract data from Zoho Invoice API and Pipedrive API', 'notes': 'Data extraction is assumed to be complete based on scope.'}, {'step': 2, 'task': 'Clean raw data', 'notes': 'Standardize date formats, remove duplicates, handle null values.'}, {'step': 3, 'task': 'Integrate datasets', 'notes': 'Join financial and sales data on customer/company IDs.'}, {'step': 4, 'task': 'Load integrated data into Google BigQuery', 'notes': 'Respect schema consistency and privacy rules.'}, {'step': 5, 'task': 'Run provided SQL queries', 'notes': 'Execute analysis SQL already provided and verify output.'}]}

    if topic and topic in mock_plans:

        plan_steps = mock_plans[topic]

    else:

        plan_steps = [{'step': 1, 'task': 'Define data sources and confirm data extraction readiness', 'notes': 'Clarify any assumptions from constraints.'}, {'step': 2, 'task': 'Perform data cleaning and transformation', 'notes': 'Ensure data quality, enforce privacy constraints.'}, {'step': 3, 'task': 'Integrate datasets as per scope requirements', 'notes': 'Consider dependencies for upstream/downstream tasks.'}, {'step': 4, 'task': 'Load final dataset to target destination', 'notes': 'Match loading schedule to given cadence.'}]

    plan_summary = f"Task Plan for: {topic or 'Generic Data Pipeline'}\n"

    plan_summary += f'Scope: {scope}\n'

    plan_summary += f'Schedule (cron): {schedule}\n'

    plan_summary += 'Constraints:\n'

    for c in constraints:

        plan_summary += f'  - {c}\n'

    plan_summary += 'Dependencies:\n'

    for d in dependencies:

        plan_summary += f'  - {d}\n'

    plan_summary += '\nBreakdown:\n'

    for step in plan_steps:

        plan_summary += f"Step {step['step']}: {step['task']} ({step['notes']})\n"

    return plan_summary
@mcp.tool()
@safe_tool
def Business_Analyst(industry_focus: str, market_scope: str, analysis_methods: str, data_sources: str, output_types: str, report_format: str, time_horizon: str) -> str:

    '''```python
    """
    Conducts market research and requirements analysis for specified industry parameters.

    This function performs an analysis based on the provided industry focus, market scope,
    analysis methods, data sources, output types, report format, and time horizon. It
    returns a detailed market analysis report or a preliminary analysis summary if specific
    data is not found.

    Args:
        industry_focus (str): The specific industry to analyze, should be seperated by space, should be one of [caregiver robots, reinforcement learning in market adaptation].
        market_scope (str): The scope of the market, should be one of [global, domestic, regional].
        analysis_methods (str): The methods used for analysis, multiple methods can be combined with ' + ', should be one of [qualitative, quantitative, predictive modeling, trend analysis]. if multiple methods are used, they should be seperated by ' + ' e.g. 'predictive modeling + trend analysis'.
        data_sources (str): The sources of data for analysis, like 'gov reports, market surveys'.
        output_types (str): The type of output required, such as 'market report'.
        report_format (str): The format of the report, should be one of [pdf, docx, ppt].
        time_horizon (str): The time frame for the analysis, like '10 years'.

    Returns:
        str: A detailed market analysis report if the specified parameters match existing data,
        otherwise a preliminary analysis summary indicating potential growth and risk factors.
    """
```'''

    mock_database = {'caregiver robots': {'global': {'qualitative + quantitative': {'gov reports, market surveys': {'market report': {'pdf': {'5 years': 'Market Analysis: Caregiver Robots - Global Elderly Care (2024-2029)\nSummary: The global caregiver robot market is projected to grow at 15% CAGR.\nDrivers: Aging population, shortage of caregivers, advances in robotics.\nDemand Analysis: High demand in Japan, EU, and North America.\nCompetitive Landscape: Key players include SoftBank Robotics, Toyota, and startups.\nOpportunities: Integration with AI assistants, home automation.\n'}}}}}}, 'reinforcement learning in market adaptation': {'global ': {'predictive modeling + trend analysis': {'transaction logs, social media sentiment': {'trend visualization': {'ppt': {'1 year': 'Analysis Report: Reinforcement Learning for Dynamic Market Adaptation (2024)\nObservations: Market fluctuations strongly correlated with seasonal consumer sentiment.\nRecommendation: Use reinforcement learning to dynamically adjust pricing and promotions.\nExpected Outcome: 8-12% increase in revenue with adaptive strategies.\n'}}}}}}}

    required_params = [industry_focus, market_scope, analysis_methods, data_sources, output_types, report_format, time_horizon]

    if not all((isinstance(param, str) and param.strip() for param in required_params)):

        raise ValueError('All parameters must be non-empty strings.')

    try:

        result = mock_database[industry_focus][market_scope][analysis_methods][data_sources][output_types][report_format][time_horizon]

        return result

    except KeyError:

        return f'Market Analysis Report\nIndustry: {industry_focus}\nScope: {market_scope}\nMethods: {analysis_methods}\nData Sources: {data_sources}\nOutput: {output_types} in {report_format} for {time_horizon}\n\nSummary: Preliminary analysis suggests stable market growth potential with moderate risk factors. Further in-depth research recommended.'
@mcp.tool()
@safe_tool
def Developer(programming_languages: str, frameworks: str, development_environment: str, hardware_integration: str, version_control: str, output_artifacts: str) -> str:

    '''```python
    """
    Manages the development process by implementing features, adhering to coding standards,
    and applying best practices for software projects.

    Args:
        programming_languages (str): A comma-separated list of programming languages used
            in the project (e.g., 'Python, C++').
        frameworks (str): A comma-separated list of frameworks utilized in the project
            (e.g., 'ROS, OpenCV').
        development_environment (str): The development environment setup, including IDE
            and operating system (e.g., 'VSCode with ROS extension, Ubuntu 20.04').
        hardware_integration (str): Details of hardware components integrated with the
            software (e.g., 'Raspberry Pi 4, Arduino Mega').
        version_control (str): The version control system employed (e.g., 'GitHub private repository').
        output_artifacts (str): The expected output artifacts from the development process
            (e.g., 'Robot control software, perception module').

    Returns:
        str: A message indicating the completion status of the development process,
        including the project name (if matched), languages, frameworks, environment,
        hardware integration, version control, output artifacts, and coding standards applied.
    """
```'''

    mock_projects = {'caregiver_robot': {'programming_languages': 'Python, C++', 'frameworks': 'ROS (Robot Operating System), OpenCV', 'development_environment': 'VSCode with ROS extension, Ubuntu 20.04', 'hardware_integration': 'Raspberry Pi 4, Arduino Mega, LiDAR, camera module', 'version_control': 'GitHub private repository', 'output_artifacts': 'Robot control software, perception module, navigation module, installation guide'}}

    if not all((isinstance(param, str) and param.strip() for param in [programming_languages, frameworks, development_environment, hardware_integration, version_control, output_artifacts])):

        raise ValueError('All parameters must be non-empty strings.')

    matched_project = None

    for (project_name, details) in mock_projects.items():

        if details['programming_languages'].lower() == programming_languages.lower() and details['frameworks'].lower() == frameworks.lower():

            matched_project = project_name

            break

    if matched_project:

        coding_standards = ['Follow PEP 8 for Python code', 'Use consistent naming conventions', 'Implement modular architecture', 'Write unit tests for all modules', 'Document public APIs using docstrings']

        return f"Development for '{matched_project}' completed successfully using {programming_languages} and {frameworks} in {development_environment}. Hardware integrated: {hardware_integration}. Version control via {version_control}. Output artifacts: {output_artifacts}. Coding standards applied: {', '.join(coding_standards)}."

    else:

        return f'New project setup completed with specified parameters. Languages: {programming_languages}, Frameworks: {frameworks}, Environment: {development_environment}, Hardware: {hardware_integration}, Version Control: {version_control}, Output: {output_artifacts}. Applied standard coding practices and best practices for implementation.'
@mcp.tool()
@safe_tool
def Tester(testing_types: str, testing_frameworks: str, performance_metrics: str, test_environment: str, reporting_format: str, output_artifacts: str) -> str:

    '''```python
    """
    Conducts quality assurance, testing, and validation processes.

    This function performs various testing types using specified frameworks,
    evaluates performance metrics, operates within a defined test environment,
    and generates reports and output artifacts in the desired format.

    Args:
        testing_types (str): A comma-separated list of testing types to be executed,
            such as 'Unit Testing', 'Integration Testing', etc.
        testing_frameworks (str): A comma-separated list of testing frameworks to be used,
            such as 'pytest', 'unittest', etc.
        performance_metrics (str): A string representation of performance metrics,
            including response time, uptime percentage, error rate, and task completion rate.
        test_environment (str): A description of the test environment setup,
            including any specific scenarios or conditions.
        reporting_format (str): The format in which test results and logs should be reported,
            e.g., 'PDF', 'CSV'.
        output_artifacts (str): A comma-separated list of artifacts to be generated as output,
            such as 'Test Summary Report', 'Defect Log', etc.

    Returns:
        str: A summary message indicating the completion of testing and validation,
            including details of the executed testing types, frameworks used, performance metrics,
            test environment, reporting format, and output artifacts.
    """
```'''

    mock_db = {'caregiver_robot_project': {'testing_types': ['Unit Testing', 'Integration Testing', 'System Testing', 'User Acceptance Testing', 'Performance Testing', 'Safety Validation'], 'testing_frameworks': ['pytest', 'unittest', 'Selenium', 'Robot Framework'], 'performance_metrics': {'response_time_ms': 250, 'uptime_percentage': 99.8, 'error_rate_percentage': 0.5, 'task_completion_rate_percentage': 97.0}, 'test_environment': 'Simulated home environment with IoT devices, obstacle scenarios, and elderly user interaction tests', 'reporting_format': 'PDF summary report with charts, CSV export of defect logs', 'output_artifacts': ['Test Summary Report', 'Defect Log', 'Performance Benchmark Report', 'Safety Compliance Certificate']}}

    for (param_name, param_value) in {'testing_types': testing_types, 'testing_frameworks': testing_frameworks, 'performance_metrics': performance_metrics, 'test_environment': test_environment, 'reporting_format': reporting_format, 'output_artifacts': output_artifacts}.items():

        if not isinstance(param_value, str) or not param_value.strip():

            raise ValueError(f"Invalid or missing value for required parameter: '{param_name}'")

    scenario_key = None

    if 'robot' in test_environment.lower() or 'home' in test_environment.lower():

        scenario_key = 'caregiver_robot_project'

    if scenario_key and scenario_key in mock_db:

        scenario_data = mock_db[scenario_key]

        return f"Testing completed successfully for scenario '{scenario_key}'.\nTesting types executed: {', '.join(scenario_data['testing_types'])}.\nFrameworks used: {', '.join(scenario_data['testing_frameworks'])}.\nPerformance metrics: {scenario_data['performance_metrics']}.\nEnvironment: {scenario_data['test_environment']}.\nReports generated in {scenario_data['reporting_format']}.\nArtifacts delivered: {', '.join(scenario_data['output_artifacts'])}."

    else:

        return 'Testing and validation completed. Reports and artifacts have been generated successfully.'
@mcp.tool()
@safe_tool
def UIUX_Expert(user_personas: str, interaction_modes: str, design_principles: str, prototyping_tools: str, usability_testing: str, output_artifacts: str) -> str:

    '''```python
    """
    Focuses on user interface and experience design by evaluating and applying
    specified design parameters to create tailored UI/UX solutions.

    Args:
        user_personas (str): A description of the target audience, including
            demographic and behavioral characteristics.
        interaction_modes (str): The methods through which users will interact
            with the system, such as voice commands or text chat.
        design_principles (str): The foundational guidelines for design,
            including aspects like accessibility and visual aesthetics.
        prototyping_tools (str): The software tools used for creating design
            prototypes, such as Figma or Adobe XD.
        usability_testing (str): The strategies employed to test the design's
            effectiveness and user satisfaction, including A/B testing and
            heuristic evaluations.
        output_artifacts (str): The final deliverables of the design process,
            such as prototypes and test reports.

    Returns:
        str: A message indicating the completion status of the UI/UX design
        process, including a summary of the applied parameters and readiness
        for stakeholder review.
    """
```'''

    mock_db = {'Design a new interaction interface for the chating robot.': {'user_personas': 'Young adults (18-35) who frequently use messaging apps, prefer quick and intuitive UI, comfortable with emojis and GIFs.', 'interaction_modes': 'Voice commands, text chat, gesture recognition.', 'design_principles': 'Minimalist design, high contrast for readability, responsive layout, accessibility compliance (WCAG 2.1).', 'prototyping_tools': 'Figma, Adobe XD, InVision.', 'usability_testing': 'A/B testing with 50 users, heuristic evaluation, think-aloud protocol.', 'output_artifacts': 'Interactive prototype, persona documentation, usability test report.'}, 'Research and analyze the market demand for caregiver robots, design a robot that can help people complete daily household activities, including market research, demand analysis, design, implementation, testing, optimization, and interactive interface.': {'user_personas': 'Elderly individuals living alone, people with mobility impairments, caregivers needing assistance.', 'interaction_modes': 'Touchscreen interface, voice commands, mobile app control.', 'design_principles': 'User-friendly navigation, large and clear icons, empathetic visual tone, multilingual support.', 'prototyping_tools': 'Sketch, Figma, Axure RP.', 'usability_testing': 'Home-based user trials, task completion time measurement, satisfaction surveys.', 'output_artifacts': 'High-fidelity mockups, interaction flow diagrams, accessibility compliance checklist.'}}

    if not all((isinstance(param, str) and param.strip() for param in [user_personas, interaction_modes, design_principles, prototyping_tools, usability_testing, output_artifacts])):

        raise ValueError('All parameters must be non-empty strings.')

    matched_scenario = None

    for (scenario, data) in mock_db.items():

        if data['user_personas'] == user_personas.strip() and data['interaction_modes'] == interaction_modes.strip():

            matched_scenario = scenario

            break

    if not matched_scenario:

        return 'UI/UX design process completed successfully with provided parameters.'

    result = f"UI/UX design for scenario: '{matched_scenario}' completed.\nUser Personas: {user_personas}\nInteraction Modes: {interaction_modes}\nDesign Principles: {design_principles}\nPrototyping Tools: {prototyping_tools}\nUsability Testing: {usability_testing}\nOutput Artifacts: {output_artifacts}\nStatus: Design ready for stakeholder review."

    return result
@mcp.tool()
@safe_tool
def obtain_business_analysis(topic: str, output_dir: str) -> str:

    '''```python
    """
    Conducts comprehensive market research and requirements analysis for a specified business topic.

    This function performs an in-depth analysis of the market trends and requirements related to the
    provided business topic or industry. The results of the analysis are saved to the specified directory.

    Args:
        topic (str): The business topic or industry focus for which the analysis is to be conducted.
                     Must be a non-empty string.
        output_dir (str): The file system path to the directory where the analysis results will be stored.
                          Must be a non-empty string.

    Returns:
        str: A confirmation message indicating that the analysis data for the specified topic has been
             successfully saved to the designated directory.
    """
```'''

    if not isinstance(topic, str) or not topic.strip():

        raise ValueError("Parameter 'topic' must be a non-empty string.")

    if not isinstance(output_dir, str) or not output_dir.strip():

        raise ValueError("Parameter 'output_dir' must be a non-empty string.")

    return f'All the analysis about {topic} is saved in {output_dir}'
@mcp.tool()
@safe_tool
def system_architecture_designer(system_design: str, technology_stack: str, hardware_requirements: str, interaction_interface: str, test_optimization_plan: str) -> str:

    '''```python
    """
    Designs high-level system architecture and plans technology strategies for various projects, including robots, websites, and simulation systems. Focuses on defining system structure, selecting technology stacks, and determining hardware/software requirements. Provides guidance for interaction design and optimization when necessary. In tasks involving multiple tools, this function exclusively manages architecture and design aspects, delegating other responsibilities to appropriate tools.
    Unable to achieve geographically related system design.
    Args:
        system_design (str): A description of the desired system architecture, detailing the structural components and their interactions.
        technology_stack (str): A specification of the technologies and frameworks to be used in the system, including frontend, backend, and database technologies.
        hardware_requirements (str): A list of hardware specifications necessary to support the system, including CPU, GPU, RAM, and storage needs.
        interaction_interface (str): A description of the user interface and interaction mechanisms, such as web UI, voice interface, or control panels.
        test_optimization_plan (str): A strategy for testing and optimizing the system, including automated tests, performance monitoring, and user feedback integration.

    Returns:
        str: A comprehensive proposal outlining the system architecture, technology stack, hardware requirements, interaction interface, and test optimization plan.
    """
```'''

    mock_architectures = {'protask_single_tool_14': {'system_design': 'A three-tier website architecture with a presentation layer (React.js SPA), application layer (Node.js REST API), and a data layer (PostgreSQL database). Includes load balancing and CDN for global availability.', 'technology_stack': 'Frontend: React.js, Backend: Node.js with Express, Database: PostgreSQL, Hosting: AWS EC2 & S3, CDN: CloudFront', 'hardware_requirements': 'Cloud-based hosting infrastructure with 2 vCPUs, 8GB RAM for application servers, and RDS instance for database.', 'interaction_interface': 'Responsive web UI with intuitive navigation, accessible design (WCAG 2.1 compliance), and interactive dashboards.', 'test_optimization_plan': 'Automated testing with Jest and Cypress, performance monitoring with New Relic, and A/B testing for UX optimization.'}, 'protask_more_seq_tools_9': {'system_design': "A modular robotics simulation system integrating MATLAB's Computer Vision Toolbox for object detection and a Java-based simulation engine (e.g., jMonkeyEngine) for realistic physics interactions. The design supports plugin-based behavior modules for autonomous decision-making.", 'technology_stack': 'MATLAB for vision algorithms, Java with jMonkeyEngine for simulation, TCP/IP for inter-process communication, JSON for data exchange.', 'hardware_requirements': 'Development workstation with multi-core CPU, dedicated GPU (e.g., NVIDIA RTX 3060), 16GB RAM, and large SSD for storing simulation assets.', 'interaction_interface': 'Simulation control panel via Java Swing UI, real-time 3D visualization, and logging console for debugging.', 'test_optimization_plan': 'Benchmarking simulation frame rates, validating object detection accuracy against test datasets, and iterative tuning of physics parameters.'}, 'protask_more_seq_tools_13': {'system_design': 'A humanoid caregiver robot architecture with modular arms, mobility base, and AI-driven control system. Includes onboard sensors for navigation and human interaction, and cloud connectivity for updates.', 'technology_stack': 'Embedded C++ for motor control, ROS (Robot Operating System) for middleware, Python for AI modules, TensorFlow for object recognition, MQTT for cloud communication.', 'hardware_requirements': 'LIDAR sensor, stereo cameras, 6-DOF robotic arms, omnidirectional wheels, onboard CPU+GPU module (e.g., NVIDIA Jetson Xavier), battery pack with 6-hour runtime.', 'interaction_interface': 'Voice interface with speech-to-text and text-to-speech, touchscreen control panel, and gesture recognition module.', 'test_optimization_plan': 'Field testing in domestic environments, motion calibration, sensor fusion optimization, and user feedback-driven iteration.'}}

    if not system_design or not technology_stack:

        raise ValueError("Both 'system_design' and 'technology_stack' parameters are required.")

    matched_key = None

    for (key, data) in mock_architectures.items():

        if system_design.lower() in data['system_design'].lower() or technology_stack.lower() in data['technology_stack'].lower():

            matched_key = key

            break

    if matched_key:

        scenario = mock_architectures[matched_key]

        return f"System Architecture Proposal:\n- System Design: {scenario['system_design']}\n- Technology Stack: {scenario['technology_stack']}\n- Hardware Requirements: {scenario.get('hardware_requirements', 'N/A')}\n- Interaction Interface: {scenario.get('interaction_interface', 'N/A')}\n- Test & Optimization Plan: {scenario.get('test_optimization_plan', 'N/A')}\n"

    else:

        return f"System Architecture Proposal:\n- System Design: {system_design}\n- Technology Stack: {technology_stack}\n- Hardware Requirements: {hardware_requirements or 'N/A'}\n- Interaction Interface: {interaction_interface or 'N/A'}\n- Test & Optimization Plan: {test_optimization_plan or 'N/A'}\n"
@mcp.tool()
@safe_tool
def octagon_companies_agent(seed_company: str, limit: int) -> str:

    '''```python
    """
    Retrieves a list of companies similar to a given reference company, limited to a specified count.

    This function identifies companies within the same business domain or industry as the provided
    seed company. It returns a curated list of potential competitors, partners, or similar businesses,
    which can be useful for competitive analysis, partnership identification, and market research.

    Args:
        seed_company (str): The name or domain of the reference company for which similar companies are sought.
            Must be a non-empty string.
        limit (int): The maximum number of similar companies to return. Must be a positive integer greater than 0.

    Returns:
        str: A JSON-formatted string containing an array of similar company names, limited to the specified count.

    Example:
        octagon_companies_agent("IBM", 3) -> '["Microsoft", "Oracle", "Accenture"]'
    """
```'''

    mock_companies_db = {'IBM': ['Microsoft', 'Oracle', 'Accenture', 'Google', 'SAP']}

    if not isinstance(seed_company, str) or not seed_company.strip():

        return "Error: 'seed_company' must be a non-empty string representing a domain or company name."

    if not isinstance(limit, int) or limit <= 0:

        return "Error: 'limit' must be a positive integer greater than 0."

    seed_company_lower = seed_company.lower().strip()

    if seed_company_lower != 'ibm':

        return f"Error: Seed company '{seed_company}' not found in the database."

    all_similar_companies = mock_companies_db['IBM']

    limited_companies = all_similar_companies[:limit]

    import json

    return json.dumps(limited_companies, indent=2)
@mcp.tool()
@safe_tool
def octagon_deepresearch_agent(companies: List[str], fields: List[str]) -> str:

    '''```python
    """
    Conduct comprehensive research on a list of companies to enhance their profiles with detailed information.
    This function enriches company profiles by providing additional context such as descriptions, leadership,
    funding, partnerships, and recent news. It complements the octagon-companies-agent by offering more nuanced
    and qualitative insights.

    Args:
        companies (List[str]): A non-empty list of company names or IDs for which detailed research is to be performed.
            All company names should be provided in lowercase in alphabetical order.
        fields (List[str]): An optional list of specific fields to include in the research results. Each field should
            be a string representing a key in the company profile. All field names should be in lowercase. List should be given in alphabetical order.
            Available fields: 'name', 'domain', 'revenue_growth', 'description', 'logo_url', 'hq_location',
            'country', 'linkedin_url', 'contact_info', 'strategic_focus'.

    Returns:
        str: A JSON-formatted string containing the enriched profiles of the specified companies. If specific fields
        are provided, only those fields will be included in the output. If a company cannot be found, an error message
        will be included in its place.
    """
```'''

    if not isinstance(companies, list) or not companies:

        raise ValueError("Parameter 'companies' must be a non-empty list of company names or IDs.")

    if fields is not None and (not isinstance(fields, list) or not all((isinstance(f, str) for f in fields))):

        raise ValueError("Parameter 'fields' must be a list of strings if provided.")

    mock_company_profiles = {'ibm': {'name': 'IBM', 'domain': 'ibm.com', 'revenue_growth': '1.5%', 'description': 'IBM is a global technology and consulting company offering infrastructure, software, and services.', 'logo_url': 'https://logo.clearbit.com/ibm.com', 'hq_location': 'Armonk, New York', 'country': 'United States', 'linkedin_url': 'https://www.linkedin.com/company/ibm', 'contact_info': {'website': 'https://www.ibm.com', 'phone': '+1-914-499-1900', 'email': 'info@ibm.com', 'address': 'One New Orchard Road, Armonk, NY 10504, USA'}, 'strategic_focus': 'Cloud computing, AI, hybrid cloud solutions, and quantum computing.'}, 'microsoft': {'name': 'Microsoft', 'domain': 'microsoft.com', 'revenue_growth': '14.0%', 'description': 'Microsoft develops, licenses, and supports a range of software products, services, and devices.', 'logo_url': 'https://logo.clearbit.com/microsoft.com', 'hq_location': 'Redmond, Washington', 'country': 'United States', 'linkedin_url': 'https://www.linkedin.com/company/microsoft', 'contact_info': {'website': 'https://www.microsoft.com', 'phone': '+1-425-882-8080', 'email': 'info@microsoft.com', 'address': 'One Microsoft Way, Redmond, WA 98052, USA'}, 'strategic_focus': 'Cloud services, AI integration, productivity software, and gaming.'}, 'google': {'name': 'Google', 'domain': 'google.com', 'revenue_growth': '8.0%', 'description': 'Google develops and provides Internet-related services and products including search, cloud computing, software and hardware.', 'logo_url': 'https://logo.clearbit.com/google.com', 'hq_location': 'Mountain View, California', 'country': 'United States', 'linkedin_url': 'https://www.linkedin.com/company/google', 'contact_info': {'website': 'https://www.google.com', 'phone': '+1-650-253-0000', 'email': 'press@google.com', 'address': '1600 Amphitheatre Parkway, Mountain View, CA 94043, USA'}, 'strategic_focus': 'Search, advertising, AI research, cloud computing, and hardware.'}, 'oracle': {'name': 'Oracle', 'domain': 'oracle.com', 'revenue_growth': '5.0%', 'description': 'Oracle offers integrated cloud applications and platform services.', 'logo_url': 'https://logo.clearbit.com/oracle.com', 'hq_location': 'Austin, Texas', 'country': 'United States', 'linkedin_url': 'https://www.linkedin.com/company/oracle', 'contact_info': {'website': 'https://www.oracle.com', 'phone': '+1-512-678-7000', 'email': 'info@oracle.com', 'address': '2300 Oracle Way, Austin, TX 78741, USA'}, 'strategic_focus': 'Database management, cloud applications, enterprise software, and AI integration.'}, 'accenture': {'name': 'Accenture', 'domain': 'accenture.com', 'revenue_growth': '3.5%', 'description': 'Accenture provides consulting, technology, and outsourcing services worldwide.', 'logo_url': 'https://logo.clearbit.com/accenture.com', 'hq_location': 'Dublin', 'country': 'Ireland', 'linkedin_url': 'https://www.linkedin.com/company/accenture', 'contact_info': {'website': 'https://www.accenture.com', 'phone': '+353-1-646-2000', 'email': 'info@accenture.com', 'address': '1 Grand Canal Square, Grand Canal Harbour, Dublin 2, Ireland'}, 'strategic_focus': 'Digital transformation, AI consulting, cloud migration, and automation services.'}, 'sap': {'name': 'SAP', 'domain': 'sap.com', 'revenue_growth': '2.5%', 'description': 'SAP is a market leader in enterprise application software, helping companies run better.', 'logo_url': 'https://logo.clearbit.com/sap.com', 'hq_location': 'Walldorf', 'country': 'Germany', 'linkedin_url': 'https://www.linkedin.com/company/sap', 'contact_info': {'website': 'https://www.sap.com', 'phone': '+49-622-777-0000', 'email': 'info@sap.com', 'address': 'Dietmar-Hopp-Allee 16, 69190 Walldorf, Germany'}, 'strategic_focus': 'Enterprise software, cloud computing, AI integration, and sustainability solutions.'}}

    result = {}

    for company in companies:

        profile = mock_company_profiles.get(company)

        if not profile:

            result[company] = {'error': 'No deep research data available for this company.'}

            continue

        if fields:

            filtered_profile = {}

            for field in fields:

                if field in profile:

                    filtered_profile[field] = profile[field]

            result[company] = filtered_profile

        else:

            result[company] = profile

    import json

    return json.dumps(result, indent=2)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

