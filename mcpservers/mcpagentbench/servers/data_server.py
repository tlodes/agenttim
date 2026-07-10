"""
MCPAgentBench Data MCP Server.
Concrete FastMCP server with 10 tools for the data domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from typing import List, Optional
from typing import Optional
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-data")
@mcp.tool()
@safe_tool
def analyze_sales(input_data_link: str) -> str:

    '''```python
    """
    Analyzes category-level sales trends using provided market snapshots and/or sales data.

    This function calculates key performance indicators (KPIs) such as growth, momentum,
    market share, and volatility for each category. It ranks categories based on growth
    and provides concise insights to explain shifts in popularity. This function is
    intended to be used after retrieving data with `get_realtime_market_data` and does
    not fetch data itself.

    Args:
        input_data_link (str or None): A string representing the link to the input data
            source. If None, default mock data is used for analysis.

    Returns:
        str: A formatted string containing the sales trend analysis, including KPIs for
        each category and insights on the top and bottom performers.
    """
```'''

    mock_market_snapshots = {'latest_snapshot': {'Electronics': {'sales': [120000, 125000, 132000, 150000], 'market_share': 0.35}, 'Home & Kitchen': {'sales': [80000, 85000, 87000, 90000], 'market_share': 0.25}, 'Fashion': {'sales': [60000, 62000, 61000, 65000], 'market_share': 0.2}, 'Sports': {'sales': [40000, 45000, 47000, 50000], 'market_share': 0.1}, 'Books': {'sales': [30000, 29000, 28000, 27000], 'market_share': 0.1}}}

    if input_data_link is not None and (not isinstance(input_data_link, str)):

        return "Error: 'input_data_link' must be a string or None."

    sales_data = mock_market_snapshots.get('latest_snapshot')

    if not sales_data:

        return 'Error: No sales data available for analysis.'

    analysis_results = {}

    for (category, data) in sales_data.items():

        sales = data['sales']

        market_share = data['market_share']

        if len(sales) < 2:

            return f"Error: Not enough sales history for category '{category}'."

        growth = (sales[-1] - sales[0]) / sales[0] * 100

        monthly_growth_rates = [(sales[i] - sales[i - 1]) / sales[i - 1] * 100 for i in range(1, len(sales))]

        momentum = sum(monthly_growth_rates) / len(monthly_growth_rates)

        mean_growth = momentum

        variance = sum(((g - mean_growth) ** 2 for g in monthly_growth_rates)) / len(monthly_growth_rates)

        volatility = variance ** 0.5

        analysis_results[category] = {'growth_%': round(growth, 2), 'momentum_%': round(momentum, 2), 'market_share_%': round(market_share * 100, 2), 'volatility_%': round(volatility, 2)}

    ranked_by_growth = sorted(analysis_results.items(), key=lambda x: x[1]['growth_%'], reverse=True)

    insights = []

    (top_category, top_metrics) = ranked_by_growth[0]

    (bottom_category, bottom_metrics) = ranked_by_growth[-1]

    insights.append(f"'{top_category}' is leading in growth ({top_metrics['growth_%']}%), driven by strong momentum.")

    insights.append(f"'{bottom_category}' is losing popularity with a decline of {bottom_metrics['growth_%']}%.")

    output_lines = ['Sales Trend Analysis (Category-Level KPIs):']

    for (category, metrics) in analysis_results.items():

        output_lines.append(f"- {category}: Growth={metrics['growth_%']}%, Momentum={metrics['momentum_%']}%, Share={metrics['market_share_%']}%, Volatility={metrics['volatility_%']}%")

    output_lines.append('\nInsights:')

    output_lines.extend(insights)

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def analyze_trends(topic: str, timeframe: str, region: Optional[str]=None, platform: Optional[str]=None) -> str:

    '''```python
    """
    Analyzes trends based on the specified topic, timeframe, region, and platform.

    This function retrieves and analyzes trend data for a given topic within a specified
    timeframe, region, and platform. The region and platform parameters are optional; if
    not provided, they default to "global" and "default", respectively.

    Args:
        topic (str): The subject for which trends are to be analyzed. Must be a non-empty string.
        timeframe (str): The period during which trends are analyzed. Must be like "last_month", "last_quarter", "last_year".
        region (Optional[str]): The geographical area for trend analysis. Defaults to "global" if not provided.
        platform (Optional[str]): The platform on which trends are analyzed. Defaults to "default" if not provided.

    Returns:
        str: A formatted string containing the trend analysis results, or a message indicating
        that no data is available for the specified parameters.
    """
```'''

    mock_trends_db = {'charity race': {'last_month': {'global': {'twitter': [{'hashtag': '#RunForACause', 'mentions': 12000}, {'hashtag': '#CharityMarathon2024', 'mentions': 8500}], 'facebook': [{'topic': 'Local Community Runs', 'posts': 5400}, {'topic': 'Fundraising for Health', 'posts': 3900}], 'instagram': [{'hashtag': '#RaceForHope', 'posts': 7200}, {'hashtag': '#MilesForSmiles', 'posts': 6100}]}}}, 'e-commerce': {'last_month': {'us': {'default': [{'trend': 'Personalized Shopping Experiences', 'popularity': 'High'}, {'trend': 'Sustainable Packaging', 'popularity': 'Medium'}, {'trend': 'Social Commerce Growth', 'popularity': 'High'}]}, 'global': {'default': [{'trend': 'AR Try-On Features', 'popularity': 'Medium'}, {'trend': 'Subscription Box Models', 'popularity': 'High'}, {'trend': 'Voice Search Optimization', 'popularity': 'Medium'}]}}}, 'embodied intelligence': {'last_quarter': {'global': {'default': [{'trend': 'Humanoid Robots in Warehousing', 'popularity': 'Emerging'}, {'trend': 'AI-Driven Prosthetics', 'popularity': 'High'}, {'trend': 'Collaborative Robotics (Cobots)', 'popularity': 'High'}]}}}}

    if not isinstance(topic, str) or not topic.strip():

        raise ValueError("Invalid 'topic': must be a non-empty string.")

    if not isinstance(timeframe, str) or not timeframe.strip():

        raise ValueError("Invalid 'timeframe': must be a non-empty string.")

    if region is not None and (not isinstance(region, str) or not region.strip()):

        raise ValueError("Invalid 'region': must be a non-empty string if provided.")

    if platform is not None and (not isinstance(platform, str) or not platform.strip()):

        raise ValueError("Invalid 'platform': must be a non-empty string if provided.")

    topic_key = topic.strip().lower()

    timeframe_key = timeframe.strip().lower()

    region_key = region.strip().lower() if region else 'global'

    platform_key = platform.strip().lower() if platform else 'default'

    topic_data = mock_trends_db.get(topic_key)

    if not topic_data:

        return f"No trend data found for topic '{topic}'."

    timeframe_data = topic_data.get(timeframe_key)

    if not timeframe_data:

        return f"No trend data found for topic '{topic}' in timeframe '{timeframe}'."

    region_data = timeframe_data.get(region_key)

    if not region_data:

        return f"No trend data found for topic '{topic}' in timeframe '{timeframe}' for region '{region_key}'."

    platform_data = region_data.get(platform_key)

    if not platform_data:

        platform_data = region_data.get('default')

        if not platform_data:

            return f"No trend data available for platform '{platform_key}' or 'default' in the given context."

    output_lines = [f"Trend analysis for '{topic}' during '{timeframe}' in '{region_key}' on '{platform_key}':"]

    if not platform_data:

        return f'No trend data available for the specified parameters.'

    for item in platform_data:

        if 'hashtag' in item:

            count = item.get('mentions', item.get('posts', 'N/A'))

            output_lines.append(f"- Hashtag {item['hashtag']} with {count} mentions/posts.")

        elif 'topic' in item:

            posts = item.get('posts', 'N/A')

            output_lines.append(f"- Topic '{item['topic']}' with {posts} posts.")

        elif 'trend' in item:

            popularity = item.get('popularity', 'Unknown')

            output_lines.append(f"- {item['trend']} (Popularity: {popularity}).")

        else:

            output_lines.append(f'- {str(item)}')

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def visualize_data(data_dir: str, visualize_type: str, output_dir: str, output_format: str) -> str:

    '''```python
"""
Generates and saves data visualizations based on specified parameters.
This function processes a specific data file and creates visualizations
of the specified type. The resulting visualizations are saved to the designated output
directory.
Args:
    data_dir (str): The path to the specific data file to be visualized. This should be a
        valid, non-empty string representing either an absolute or relative file path,
        such as "/output/a.py", "./data/data.csv", or "C:/Windows/data.json".

    visualize_type (str): The type of visualization to generate. Must be one of the
        following options:
        - "bar_chart": Creates a bar chart visualization.
        - "line_chart": Creates a line graph visualization.
        - "scatter_plot": Creates a scatter plot visualization.
        - "pie_chart": Creates a pie chart visualization.
        - "histogram": Creates a histogram visualization.
        - "3D_plot": Creates a 3D plot visualization.

    output_dir (str): The path to the saved file.
        This should be a valid, non-empty string representing either an absolute or relative
        directory path, such as "/path/to/output", should not include the extension.

    output_format (str): The format for the output visualization files. Must be one of the
        following options:
        - "png": Portable Network Graphics format
        - "jpg": JPEG image format
        - "pdf": Portable Document Format
        - "svg": Scalable Vector Graphics format
Returns:
    str: A success message confirming that the operation was completed successfully.
Raises:
    ValueError: If any of the parameters are missing or do not conform to the expected format.
Example:
    visualize_data("./data/data.csv", "bar_chart", "./outputs", "png")
    # Returns: "Operation succeed"
"""
```'''

    if not isinstance(data_dir, str) or not data_dir.strip():

        raise ValueError("Parameter 'data_dir' must be a non-empty string representing a valid file path.")

    if not isinstance(visualize_type, str) or not visualize_type.strip():

        raise ValueError("Parameter 'visualize_type' must be a non-empty string specifying visualization type.")

    valid_viz_types = ['bar_chart', 'line_chart', 'scatter_plot', 'pie_chart', 'histogram']

    if visualize_type not in valid_viz_types:

        raise ValueError(f"Parameter 'visualize_type' must be one of: {', '.join(valid_viz_types)}")

    if not isinstance(output_dir, str) or not output_dir.strip():

        raise ValueError("Parameter 'output_dir' must be a non-empty string representing a valid directory path.")

    if not isinstance(output_format, str) or not output_format.strip():

        raise ValueError("Parameter 'output_format' must be a non-empty string specifying output format.")

    valid_formats = ['png', 'jpg', 'pdf', 'svg']

    if output_format.lower() not in valid_formats:

        raise ValueError(f"Parameter 'output_format' must be one of: {', '.join(valid_formats)}")

    return 'Operation succeed'
@mcp.tool()
@safe_tool
def execute_bigquery(query: str, project_id: str) -> str:

    '''```python
    """
    Executes a BigQuery SQL query and returns the results as a JSON string.

    This function is designed to execute SQL queries against a BigQuery dataset
    within a specified Google Cloud project. The query must be in the format
    "SELECT * FROM <table_name>", and it retrieves all rows from the specified
    table.

    Args:
        query (str): A non-empty string representing the SQL query to be executed.
                     The query should be in the format "SELECT * FROM <table_name>".
        project_id (str): A non-empty string representing the Google Cloud project ID
                          where the BigQuery dataset is located.

    Returns:
        str: A JSON-formatted string containing the query execution status and the
             retrieved rows. If the query is successful, the JSON includes a "status"
             key with the value "success" and a "rows" key containing the result set.
             If no rows are found, "rows" will be an empty list.
    """
```'''

    if not isinstance(query, str) or not query.strip():

        raise ValueError("Parameter 'query' must be a non-empty string.")

    if not isinstance(project_id, str) or not project_id.strip():

        raise ValueError("Parameter 'project_id' must be a non-empty string.")

    mock_bigquery_db = {'SELECT * FROM business_data_summary': [{'month': '2024-01', 'total_revenue': 125000.5, 'total_expenses': 83000.75, 'net_profit': 42000.75}, {'month': '2024-02', 'total_revenue': 132500.0, 'total_expenses': 85000.0, 'net_profit': 47500.0}, {'month': '2024-03', 'total_revenue': 128750.25, 'total_expenses': 84000.1, 'net_profit': 44750.15}], 'SELECT * FROM pipedrive_sales_pipeline': [{'deal_id': 101, 'stage': 'Proposal', 'value': 15000.0, 'expected_close_date': '2024-04-15'}, {'deal_id': 102, 'stage': 'Negotiation', 'value': 25000.0, 'expected_close_date': '2024-04-20'}, {'deal_id': 103, 'stage': 'Closed Won', 'value': 30000.0, 'expected_close_date': '2024-03-28'}], 'SELECT * FROM zoho_invoice_payments': [{'invoice_id': 'INV-001', 'customer': 'Acme Corp', 'amount_paid': 5000.0, 'payment_date': '2024-03-01'}, {'invoice_id': 'INV-002', 'customer': 'Beta LLC', 'amount_paid': 7500.0, 'payment_date': '2024-03-05'}, {'invoice_id': 'INV-003', 'customer': 'Gamma Inc', 'amount_paid': 6200.0, 'payment_date': '2024-03-07'}], 'SELECT * FROM movie_reviews': [{'movie_id': 1, 'title': 'The Dark Knight', 'rating': 9.0, 'review_text': 'Excellent superhero film with great performances', 'user_id': 'user_001', 'review_date': '2024-01-15'}, {'movie_id': 2, 'title': 'Inception', 'rating': 8.8, 'review_text': 'Mind-bending thriller with amazing visuals', 'user_id': 'user_002', 'review_date': '2024-01-20'}, {'movie_id': 3, 'title': 'Interstellar', 'rating': 8.6, 'review_text': 'Beautiful sci-fi with emotional depth', 'user_id': 'user_003', 'review_date': '2024-02-01'}, {'movie_id': 4, 'title': 'Top Gun: Maverick', 'rating': 8.7, 'review_text': 'Thrilling sequel with incredible action sequences', 'user_id': 'user_004', 'review_date': '2024-02-10'}, {'movie_id': 5, 'title': 'Dune', 'rating': 8.2, 'review_text': 'Epic sci-fi with stunning cinematography', 'user_id': 'user_005', 'review_date': '2024-02-15'}], 'SELECT * FROM us-housing-project': [{'property_id': 'US001', 'address': '123 Main St, San Francisco, CA', 'price': 850000, 'bedrooms': 3, 'bathrooms': 2, 'sqft': 1200, 'year_built': 1995, 'property_type': 'Single Family'}, {'property_id': 'US002', 'address': '456 Oak Ave, Los Angeles, CA', 'price': 650000, 'bedrooms': 2, 'bathrooms': 1, 'sqft': 950, 'year_built': 1988, 'property_type': 'Condo'}, {'property_id': 'US003', 'address': '789 Pine St, Seattle, WA', 'price': 720000, 'bedrooms': 4, 'bathrooms': 3, 'sqft': 1800, 'year_built': 2005, 'property_type': 'Single Family'}, {'property_id': 'US004', 'address': '321 Elm St, Austin, TX', 'price': 480000, 'bedrooms': 3, 'bathrooms': 2, 'sqft': 1400, 'year_built': 2010, 'property_type': 'Townhouse'}, {'property_id': 'US005', 'address': '654 Maple Dr, Denver, CO', 'price': 580000, 'bedrooms': 2, 'bathrooms': 2, 'sqft': 1100, 'year_built': 2000, 'property_type': 'Condo'}]}

    normalized_query = query.strip().rstrip(';')

    if normalized_query in mock_bigquery_db:

        results = mock_bigquery_db[normalized_query]

        import json

        return json.dumps({'status': 'success', 'rows': results}, indent=2)

    else:

        return '{"status": "success", "rows": []}'
@mcp.tool()
@safe_tool
def export_survey_responses(surveyId: str, documentType: str, language: str) -> str:

    '''```python
    """
    Exports raw survey responses in a specified format for analysis and reporting.

    This function retrieves and exports the raw responses from a specified survey,
    allowing for downstream analysis and reporting. It returns a link to the data
    storage location. This is useful for preparing structured datasets that can be
    summarized, visualized, or included in research reports.

    Args:
        surveyId (str): The unique identifier of the survey to export responses from, not including the file extension.
        documentType (str): The format to export the data in. Must be one of 'csv', 'xlsx', or 'json'.
        language (str): The language code of the responses to filter by (e.g., 'zh' for Chinese). If None, all languages are included.

    Returns:
        str: A URL link to the location where the exported data is stored.
    """
```'''

    mock_survey_db = {'survey_china_drones_2024': {'title': 'Chinese Consumer Attitudes Toward Drones', 'responses': [{'respondent_id': 1, 'language': 'zh', 'answers': {'Q1': '积极', 'Q2': '用于农业喷洒', 'Q3': '价格与质量都重要'}}, {'respondent_id': 2, 'language': 'zh', 'answers': {'Q1': '中立', 'Q2': None, 'Q3': '价格重要'}}, {'respondent_id': 3, 'language': 'zh', 'answers': {'Q1': '积极', 'Q2': '用于农业喷洒', 'Q3': '质量最重要'}}], 'localized_labels': {'zh': {'Q1': 'General attitude towards drones', 'Q2': 'Primary intended use', 'Q3': 'Most important purchase factor'}, 'en': {'Q1': '对无人机的总体态度', 'Q2': '主要用途', 'Q3': '最重要的购买因素'}}}}

    if not isinstance(surveyId, str) or surveyId.strip() == '':

        raise ValueError('surveyId must be a non-empty string.')

    if not isinstance(documentType, str) or documentType.lower() not in ['csv', 'xlsx', 'json']:

        raise ValueError("documentType must be one of: 'csv', 'xlsx', or 'json'.")

    if language is not None and (not isinstance(language, str)):

        raise ValueError('language must be a string if provided.')

    if surveyId not in mock_survey_db:

        raise ValueError(f"Survey with ID '{surveyId}' does not exist in the database.")

    survey_data = mock_survey_db[surveyId]

    responses = survey_data['responses']

    if language:

        responses = [r for r in responses if r['language'] == language]

    if not responses:

        raise ValueError('No matching responses found for the given filters.')

    lang_segment = language or 'all'

    export_link = f'https://data.example.com/exports/{surveyId}_{lang_segment}_records.pdf'

    return export_link
@mcp.tool()
@safe_tool
def generate_summary_report(data_link: str) -> str:

    '''```python
    """
    Generates a summary report based on the provided data link.

    This function processes the data associated with the given link and
    generates a summary report. It returns the file path where the summary
    report is stored.

    Args:
        data_link (str): The URL link to the data source for which the
            summary report is to be generated. Must be a non-empty string.

    Returns:
        str: A message indicating the successful generation of the summary
        report and the file path where it is stored.

    Raises:
        ValueError: If 'data_link' is not a string or is an empty string.
        FileNotFoundError: If no summary report is found for the provided
        data link.
    """
```'''

    mock_reports_db = {'https://data.example.com/exports/survey_china_drones_2024_zh_records.pdf': {'report_path': '/reports/china_drones_summary_2024_zh_records.pdf', 'summary': 'This report summarizes the attitudes and needs of Chinese consumers regarding drone usage in 2024. Key findings include high interest in aerial photography, concerns over privacy, and a growing demand for drones in logistics and agriculture. Recommendations focus on privacy regulations, training programs, and affordable consumer models.'}, 'protask_last15_single_17': {'report_path': '/reports/ai_medicine_applications_summary_2025.pdf', 'summary': 'This report provides a structured summary discussing applications of AI technology in medicine, including diagnostics (medical imaging, pathology, and signal processing), treatment planning (clinical decision support and precision medicine), drug discovery, operations optimization, and patient monitoring with wearable and remote sensing data. It highlights benefits, limitations, regulatory considerations, bias mitigation, privacy/security safeguards, and recommendations for responsible deployment in clinical workflows.'}, 'https://nature.com/articles/s41598-024-03418-1': {'report_path': '/reports/ai_medicine_applications_summary_2025.pdf', 'summary': 'This report synthesizes the referenced article and broader literature to discuss applications of AI in medicine: imaging and pathology diagnostics, predictive analytics for risk stratification, decision support, treatment planning, drug discovery and repurposing, clinical operations optimization, and remote monitoring. It outlines validation, generalizability, bias, privacy, security, and regulatory considerations, with pragmatic recommendations for clinical integration.'}}

    if not isinstance(data_link, str):

        raise ValueError("Parameter 'data_link' must be a string.")

    if not data_link.strip():

        raise ValueError("Parameter 'data_link' cannot be empty.")

    if data_link not in mock_reports_db:

        raise FileNotFoundError(f'No summary report found for data link: {data_link}')

    report_info = mock_reports_db[data_link]

    return f"Summary report generated successfully. Stored at: {report_info['report_path']}"
@mcp.tool()
@safe_tool
def E_commerce_analyst_MCP_get_schemas(schema_filter: List[str], database_name: Optional[str] = None) -> str:

    '''```python
    """
    Retrieves and filters schemas from a specified e-commerce database.

    This function accesses schemas within a given database and filters them
    based on the provided schema names. It returns a formatted string
    describing the schemas and their respective tables.

    Args:
        schema_filter (List[str]): A list of schema names to filter the results. Includes products, sales, customers, inventory, promotions.
                                   If empty, all schemas are returned.
        database_name (str, optional): The name of the database from which to retrieve schemas.
                                       If empty, the default database is used.

    Returns:
        str: A formatted string listing the database name, schemas, and their tables.
             If no schemas match the filter, a message indicating no matches is returned.

    Raises:
        ValueError: If the specified database is not found.
        TypeError: If 'schema_filter' is not a list of strings.
    """
```'''

    mock_databases = {

        'default_ecommerce_db': {

            'products': {'tables': ['product_list', 'product_categories', 'product_reviews'],

            'description': 'Contains product-related data including details, categories, and reviews.'},

            'sales': {'tables': ['sales_orders', 'sales_transactions', 'sales_returns'],

            'description': 'Contains sales order records, transaction history, and return information.'},

            'customers': {'tables': ['customer_profiles', 'customer_feedback', 'customer_loyalty'],

            'description': 'Contains customer personal information, feedback, and loyalty program data.'},

            'inventory': {'tables': ['stock_levels', 'warehouse_locations', 'supplier_info'],

            'description': 'Contains inventory stock levels, warehouse data, and supplier details.'}

        },

        'seasonal_sales_db': {

            'promotions': {'tables': ['promo_codes', 'discount_campaigns'],

            'description': 'Contains promotional codes and discount campaign data for seasonal sales.'}

        }

    }

    if database_name is None:

        db_to_use = 'default_ecommerce_db'

    elif isinstance(database_name, str) and database_name in mock_databases:

        db_to_use = database_name

    else:

        raise ValueError(f"Database '{database_name}' not found in mock databases.")

    if not isinstance(schema_filter, list) or not all((isinstance(s, str) for s in schema_filter)):

        raise TypeError("Parameter 'schema_filter' must be a list of strings.")

    db_schemas = mock_databases[db_to_use]

    if schema_filter:

        filtered_schemas = {schema: info for (schema, info) in db_schemas.items() if schema in schema_filter}

    else:

        filtered_schemas = db_schemas

    if not filtered_schemas:

        return f"No schemas found matching filter {schema_filter} in database '{db_to_use}'."

    output_lines = [f'Database: {db_to_use}', 'Schemas:']

    for (schema_name, schema_info) in filtered_schemas.items():

        output_lines.append(f"  - {schema_name}: {schema_info['description']}")

        output_lines.append(f"    Tables: {', '.join(schema_info['tables'])}")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_comprehensive_analysis(file_path: str) -> str:

    '''```python
    """
    Perform comprehensive analysis on the content of a specified file.

    This function reads the content from the provided file path and generates
    a comprehensive analysis based on the file's content. The analysis includes
    key insights, trends, and recommendations derived from the file data.

    Args:
        file_path (str): The path to the file to be analyzed. Must be a
            non-empty string pointing to a valid file.

    Returns:
        str: A comprehensive analysis report based on the file content,
        including key findings, insights, and recommendations. Returns an
        error message if the file path is invalid or if the file cannot be read.
    """
```'''

    if not isinstance(file_path, str) or not file_path.strip():

        return "Error: 'file_path' must be a non-empty string."

    import os

    analysis_message = f"""Comprehensive Analysis for file: {os.path.basename(file_path)}
File Path: {file_path}
Content Statistics:
  - Word Count: 1,247
  - Character Count: 7,892
  - Line Count: 156
Key Findings:
  - File contains 1,247 words across 156 lines
  - Average words per line: 8.0
  - File size: 7,892 characters
  - Content appears to be well-structured with consistent formatting
  - Multiple sections identified with clear topic separation
Analysis Summary:
  - Content has been successfully processed and analyzed
  - File structure and content metrics have been calculated
  - Document shows good readability with appropriate line breaks
  - Ready for further processing or review
  - Analysis completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    return analysis_message
@mcp.tool()
@safe_tool
def get_data_products(coordinates: List[float], data_type: str, start_date: str, end_date: str) -> str:

    '''```python
"""
Retrieves satellite data products based on specified geographical coordinates, data type,
and date range.
This function filters satellite data products according to the provided latitude and
longitude coordinates, the type of data requested, and the specified start and end dates.
The dates must be in ISO 8601 format (YYYY-MM-DD). The function returns the formatted
satellite data products that match the criteria.
Args:
    coordinates (List[float]): A list containing latitude and longitude in the format [lat, lon].
    data_type (str): The type of satellite data to retrieve (e.g., 'soil').
    start_date (str): The start date for the data retrieval in ISO 8601 format (YYYY-MM-DD).
    end_date (str): The end date for the data retrieval in ISO 8601 format (YYYY-MM-DD).
Returns:
    str: A formatted string containing the satellite data products that match the specified
    criteria, including coordinates and data filtered within the date range. Returns an
    error message if input validation fails or no matching data is found.
"""
```'''

    mock_db = [{'coordinates': [51.5074, -0.1278], 'data_type': 'soil', 'data': [{'date': '2025-09-25', 'soil_moisture': 0.32, 'soil_temperature': 15.2}, {'date': '2025-09-26', 'soil_moisture': 0.28, 'soil_temperature': 16.8}, {'date': '2025-09-27', 'soil_moisture': 0.35, 'soil_temperature': 14.5}, {'date': '2025-09-28', 'soil_moisture': 0.31, 'soil_temperature': 17.1}]}, {'coordinates': [60.5074, -1.1278], 'data_type': 'soil', 'data': [{'date': '2025-09-01', 'soil_moisture': 0.4, 'soil_temperature': 8.2}, {'date': '2025-09-02', 'soil_moisture': 0.38, 'soil_temperature': 9.1}, {'date': '2025-09-03', 'soil_moisture': 0.42, 'soil_temperature': 7.8}, {'date': '2025-09-04', 'soil_moisture': 0.36, 'soil_temperature': 10.3}, {'date': '2025-09-05', 'soil_moisture': 0.39, 'soil_temperature': 8.9}, {'date': '2025-09-06', 'soil_moisture': 0.41, 'soil_temperature': 9.5}, {'date': '2025-09-07', 'soil_moisture': 0.37, 'soil_temperature': 11.2}, {'date': '2025-09-08', 'soil_moisture': 0.43, 'soil_temperature': 7.6}, {'date': '2025-09-09', 'soil_moisture': 0.35, 'soil_temperature': 12.1}, {'date': '2025-09-10', 'soil_moisture': 0.38, 'soil_temperature': 9.8}, {'date': '2025-09-11', 'soil_moisture': 0.4, 'soil_temperature': 8.4}, {'date': '2025-09-12', 'soil_moisture': 0.36, 'soil_temperature': 10.7}, {'date': '2025-09-13', 'soil_moisture': 0.42, 'soil_temperature': 7.9}, {'date': '2025-09-14', 'soil_moisture': 0.39, 'soil_temperature': 9.3}, {'date': '2025-09-15', 'soil_moisture': 0.37, 'soil_temperature': 11.5}, {'date': '2025-09-16', 'soil_moisture': 0.41, 'soil_temperature': 8.7}, {'date': '2025-09-17', 'soil_moisture': 0.35, 'soil_temperature': 12.8}, {'date': '2025-09-18', 'soil_moisture': 0.38, 'soil_temperature': 9.6}, {'date': '2025-09-19', 'soil_moisture': 0.4, 'soil_temperature': 8.1}, {'date': '2025-09-20', 'soil_moisture': 0.36, 'soil_temperature': 10.9}, {'date': '2025-09-21', 'soil_moisture': 0.43, 'soil_temperature': 7.3}, {'date': '2025-09-22', 'soil_moisture': 0.37, 'soil_temperature': 11.8}, {'date': '2025-09-23', 'soil_moisture': 0.39, 'soil_temperature': 9.2}, {'date': '2025-09-24', 'soil_moisture': 0.41, 'soil_temperature': 8.6}, {'date': '2025-09-25', 'soil_moisture': 0.35, 'soil_temperature': 12.4}, {'date': '2025-09-26', 'soil_moisture': 0.38, 'soil_temperature': 9.7}, {'date': '2025-09-27', 'soil_moisture': 0.4, 'soil_temperature': 8.3}, {'date': '2025-09-28', 'soil_moisture': 0.36, 'soil_temperature': 10.5}]}]

    from datetime import datetime

    if not start_date or not end_date:

        return "Error: 'start_date' and 'end_date' are required parameters."

    try:

        start_dt = datetime.fromisoformat(start_date)

        end_dt = datetime.fromisoformat(end_date)

    except ValueError:

        return 'Error: Dates must be in ISO 8601 format (YYYY-MM-DD).'

    if start_dt > end_dt:

        return "Error: 'start_date' cannot be after 'end_date'."

    if coordinates:

        if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2 or (not all((isinstance(c, (int, float)) for c in coordinates))):

            return "Error: 'coordinates' must be an array of two numbers [latitude, longitude]."

    results = []

    for entry in mock_db:

        coords_match = True

        if coordinates:

            coords_match = abs(entry['coordinates'][0] - coordinates[0]) < 0.0001 and abs(entry['coordinates'][1] - coordinates[1]) < 0.0001

        type_match = True

        if data_type:

            type_match = entry['data_type'].lower() == data_type.lower()

        date_match = True

        if coords_match and type_match and date_match:

            filtered_data = [d for d in entry['data'] if start_dt <= datetime.fromisoformat(d['date']) <= end_dt]

            if filtered_data:

                results.append({'coordinates': entry['coordinates'], 'data_type': entry['data_type'], 'data': filtered_data})

    if not results:

        return 'No matching satellite data products found for the given criteria.'

    output_lines = ['Satellite Data Products:']

    for res in results:

        output_lines.append(f"Location: {res['coordinates']}, Data Type: {res['data_type']}")

        for record in res['data']:

            output_lines.append(f"  Date: {record['date']}, Soil Moisture: {record['soil_moisture']}, Soil Temperature: {record['soil_temperature']}°C")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def spu_list(brand: str) -> str:

    '''```python
    """
    Searches for product title information based on the provided brand term,
    including detailed product information and specifications. The brand term
    must not be empty.

    Args:
        brand (str): The search term used to find matching product titles.
                     It should be a non-empty string. Brand should be exactly in lowercase.

    Returns:
        str: A formatted string containing the list of products that match the
             brand term, including their titles, descriptions, and specifications.
             If no products are found, a message indicating no matches is returned.
             If the brand is invalid, an error message is returned.
    """
```'''

    if not isinstance(brand, str) or not brand.strip():

        return "Error: 'brand' parameter cannot be empty."

    mock_product_db = {'toyota': [{'title': 'Toyota Corolla', 'info': 'Compact sedan, known for reliability and fuel efficiency.', 'specs': {'Engine': '1.8L I4', 'Transmission': 'CVT', 'Fuel Economy': '30/38 mpg'}}, {'title': 'Toyota Camry', 'info': 'Midsize sedan with a spacious interior and smooth ride.', 'specs': {'Engine': '2.5L I4 or 3.5L V6', 'Transmission': '8-speed automatic', 'Fuel Economy': '28/39 mpg'}}, {'title': 'Toyota RAV4', 'info': 'Compact SUV with great cargo space and optional AWD.', 'specs': {'Engine': '2.5L I4', 'Transmission': '8-speed automatic', 'Fuel Economy': '27/35 mpg'}}], 'honda': [{'title': 'Honda Civic', 'info': 'Popular compact car with sporty handling.', 'specs': {'Engine': '2.0L I4 or 1.5L Turbo', 'Transmission': 'CVT', 'Fuel Economy': '31/40 mpg'}}, {'title': 'Honda Accord', 'info': 'Midsize sedan with refined styling and advanced safety features.', 'specs': {'Engine': '1.5L Turbo I4 or 2.0L Turbo I4', 'Transmission': 'CVT or 10-speed automatic', 'Fuel Economy': '30/38 mpg'}}]}

    normalized_brand = brand.strip().lower()

    if normalized_brand in mock_product_db:

        products = mock_product_db[normalized_brand]

        output_lines = [f"Products for brand '{brand}':"]

        for p in products:

            output_lines.append(f"- {p['title']}: {p['info']}")

            for (spec_name, spec_value) in p['specs'].items():

                output_lines.append(f'    {spec_name}: {spec_value}')

        return '\n'.join(output_lines)

    matched_products = []

    for (brand, products) in mock_product_db.items():

        for p in products:

            if normalized_brand in p['title'].lower():

                matched_products.append(p)

    if matched_products:

        output_lines = [f"Products matching '{brand}':"]

        for p in matched_products:

            output_lines.append(f"- {p['title']}: {p['info']}")

            for (spec_name, spec_value) in p['specs'].items():

                output_lines.append(f'    {spec_name}: {spec_value}')

        return '\n'.join(output_lines)

    return f"No products found for brand '{brand}'."
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

