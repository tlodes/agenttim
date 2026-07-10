"""
MCPAgentBench Finance MCP Server.
Concrete FastMCP server with 8 tools for the finance domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from typing import List, Optional
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-finance")
@mcp.tool()
@safe_tool
def get_balance(account_type: str) -> str:

    '''"""
Check the balance for a specified account type.
The account type must be either "checking" or "savings". This function returns
a formatted string indicating the current balance for the selected account.
Args:
    account_type (str): The type of account to check. Must be either
        "checking" or "savings".
Returns:
    str: A message stating the balance of the specified account in USD.
"""'''

    mock_balance = {'checking': 1500, 'savings': 3000}

    return f"The balance of the user's {account_type} account is {mock_balance[account_type]} USD."
@mcp.tool()
@safe_tool
def send_transaction(target: str, amount: float) -> str:

    '''"""
Send a transaction to a specified target with a specified amount.
Args:
    target (str): The recipient of the transaction, must be only the name of the recipient. For example, "Tomas" is valid, but "Mr. Tomas" is not.
    amount (float): The amount of money to send, in USD.
Returns:
    str: A confirmation message indicating that the transaction was successful.
"""'''

    return f'Transaction successful! The {target} received {amount} USD.'
@mcp.tool()
@safe_tool
def get_market_index(indices: List[str]) -> str:

    '''```python
    """
    Retrieve data for specified major stock indices.

    This function provides information on major stock indices such as the
    Shanghai Stock Exchange Index, Shenzhen Stock Exchange Component Index,
    ChiNext Index, STAR Market 50, CSI 300, and CSI 500. It returns the latest
    closing values, daily changes, percentage changes, and market trends for
    the requested indices.

    Args:
        indices (List[str]): A list of index codes representing the stock
            indices for which data is requested. Valid index codes include:
            'SHCOMP' (Shanghai Composite Index), 'SZCOMP' (Shenzhen Component Index),
            'STAR50' (STAR Market 50 Index), 'CSI300' (CSI 300 Index), 'CSI500' (CSI 500 Index).
            If None, data for all available indices will be returned.

    Returns:
        str: A formatted string containing the latest data for each requested
        index, including the index name, latest closing value, change,
        percentage change, trend, and the date of the data.
    """
```'''

    mock_indices_data = {'SHCOMP': {'name': 'Shanghai Composite Index', 'latest_close': 3225.14, 'change': -0.42, 'change_percent': -0.013, 'trend': 'slight downward in recent sessions due to profit-taking after a short rally', 'date': '2024-06-10'}, 'SZCOMP': {'name': 'Shenzhen Component Index', 'latest_close': 10875.56, 'change': 0.78, 'change_percent': 0.0072, 'trend': 'mild upward momentum led by technology and consumer sectors', 'date': '2024-06-10'}, 'CHINEXT': {'name': 'ChiNext Index', 'latest_close': 2295.67, 'change': 1.25, 'change_percent': 0.0055, 'trend': 'gradual recovery driven by innovation and biotech companies', 'date': '2024-06-10'}, 'STAR50': {'name': 'STAR Market 50 Index', 'latest_close': 1025.78, 'change': -2.14, 'change_percent': -0.0205, 'trend': 'declining due to high valuation concerns in semiconductor stocks', 'date': '2024-06-10'}, 'CSI300': {'name': 'CSI 300 Index', 'latest_close': 3995.25, 'change': -0.85, 'change_percent': -0.0021, 'trend': 'sideways movement with mixed performance in financials and consumer staples', 'date': '2024-06-10'}, 'CSI500': {'name': 'CSI 500 Index', 'latest_close': 5980.45, 'change': 1.02, 'change_percent': 0.0017, 'trend': 'steady gains supported by mid-cap industrial and energy companies', 'date': '2024-06-10'}}

    if indices is not None:

        if not isinstance(indices, list):

            return "Error: 'indices' parameter must be a list of index codes."

        invalid_codes = [code for code in indices if code not in mock_indices_data]

        if invalid_codes:

            return f"Error: Invalid index codes provided: {', '.join(invalid_codes)}"

        selected_data = {code: mock_indices_data[code] for code in indices}

    else:

        selected_data = mock_indices_data

    output_lines = []

    for (code, data) in selected_data.items():

        line = f"{data['name']} ({code}) - Latest Close: {data['latest_close']}, Change: {data['change']} ({data['change_percent'] * 100:.2f}%), Trend: {data['trend']} (as of {data['date']})"

        output_lines.append(line)

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_market_summary(filter_type: list, filter_count: str, start_date: str, end_date: str) -> str:

    '''```python
"""
Retrieves a summary of KRW cryptocurrency markets with options to filter results based on popularity, visit frequency, and new listings.
Args:
    filter_type (list of str): A list of filter criteria to apply. Valid options are "popular", "most_visited", and "new_listing".
    filter_count (str): The number of results to return for each specified filter type. Must be a positive integer.
    start_date (str): The start date for filtering new listings, in the format 'YYYY-MM-DD'.
    end_date (str): The end date for filtering new listings, in the format 'YYYY-MM-DD'.
Returns:
    str: A formatted string containing the market summary with results filtered according to the specified criteria.
"""
```'''

    mock_market_data = [{'market': 'KRW-BTC', 'name': 'Bitcoin', 'volume_24h': 25000000000, 'visits': 120000, 'listed_days_ago': 1500, 'listing_date': '2021-01-01'}, {'market': 'KRW-ETH', 'name': 'Ethereum', 'volume_24h': 15000000000, 'visits': 95000, 'listed_days_ago': 1400, 'listing_date': '2021-02-01'}, {'market': 'KRW-XRP', 'name': 'Ripple', 'volume_24h': 8000000000, 'visits': 88000, 'listed_days_ago': 1300, 'listing_date': '2021-03-01'}, {'market': 'KRW-ADA', 'name': 'Cardano', 'volume_24h': 6000000000, 'visits': 72000, 'listed_days_ago': 1200, 'listing_date': '2021-04-01'}, {'market': 'KRW-DOGE', 'name': 'Dogecoin', 'volume_24h': 5500000000, 'visits': 68000, 'listed_days_ago': 1100, 'listing_date': '2021-05-01'}, {'market': 'KRW-SOL', 'name': 'Solana', 'volume_24h': 5000000000, 'visits': 64000, 'listed_days_ago': 100, 'listing_date': '2024-06-01'}, {'market': 'KRW-DOT', 'name': 'Polkadot', 'volume_24h': 4200000000, 'visits': 58000, 'listed_days_ago': 900, 'listing_date': '2021-07-01'}, {'market': 'KRW-MATIC', 'name': 'Polygon', 'volume_24h': 3800000000, 'visits': 55000, 'listed_days_ago': 800, 'listing_date': '2021-08-01'}, {'market': 'KRW-APT', 'name': 'Aptos', 'volume_24h': 3600000000, 'visits': 53000, 'listed_days_ago': 30, 'listing_date': '2025-08-28'}, {'market': 'KRW-ARB', 'name': 'Arbitrum', 'volume_24h': 3400000000, 'visits': 52000, 'listed_days_ago': 10, 'listing_date': '2025-09-17'}, {'market': 'KRW-SUI', 'name': 'Sui', 'volume_24h': 3200000000, 'visits': 48000, 'listed_days_ago': 5, 'listing_date': '2025-09-22'}, {'market': 'KRW-OP', 'name': 'Optimism', 'volume_24h': 3000000000, 'visits': 45000, 'listed_days_ago': 3, 'listing_date': '2025-09-24'}, {'market': 'KRW-BASE', 'name': 'Base', 'volume_24h': 2800000000, 'visits': 42000, 'listed_days_ago': 1, 'listing_date': '2025-09-26'}, {'market': 'KRW-LINK', 'name': 'Chainlink', 'volume_24h': 4500000000, 'visits': 62000, 'listed_days_ago': 800, 'listing_date': '2021-09-01'}, {'market': 'KRW-UNI', 'name': 'Uniswap', 'volume_24h': 4000000000, 'visits': 60000, 'listed_days_ago': 700, 'listing_date': '2021-10-01'}]

    try:

        filter_count_int = int(filter_count)

    except ValueError:

        return "Error: 'filter_count' must be a valid integer."

    if filter_count_int <= 0:

        return "Error: 'filter_count' must be greater than 0."

    valid_filters = ['popular', 'most_visited', 'new_listing']

    for filter_t in filter_type:

        if filter_t not in valid_filters:

            return f"Error: Invalid filter type '{filter_t}'. Must be one of {valid_filters}."

    from datetime import datetime

    try:

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')

        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    except ValueError:

        return 'Error: Dates must be in YYYY-MM-DD format.'

    if start_dt > end_dt:

        return "Error: 'start_date' cannot be after 'end_date'."

    output_lines = []

    output_lines.append('KRW Market Summary:')

    output_lines.append('=' * 50)

    if 'popular' in filter_type:

        popular_data = sorted(mock_market_data, key=lambda x: x['volume_24h'], reverse=True)[:filter_count_int]

        output_lines.append(f'\nTop {filter_count_int} Popular Cryptocurrencies (by Volume):')

        for (i, coin) in enumerate(popular_data, 1):

            output_lines.append(f"{i}. {coin['name']} ({coin['market']}): ₩{coin['volume_24h']:,}")

    if 'most_visited' in filter_type:

        visited_data = sorted(mock_market_data, key=lambda x: x['visits'], reverse=True)[:filter_count_int]

        output_lines.append(f'\nTop {filter_count_int} Most Visited Coins:')

        for (i, coin) in enumerate(visited_data, 1):

            output_lines.append(f"{i}. {coin['name']} ({coin['market']}): {coin['visits']:,} visits")

    if 'new_listing' in filter_type:

        new_listings = []

        for coin in mock_market_data:

            coin_date = datetime.strptime(coin['listing_date'], '%Y-%m-%d')

            if start_dt <= coin_date <= end_dt:

                new_listings.append(coin)

        new_listings = sorted(new_listings, key=lambda x: x['listing_date'], reverse=True)[:filter_count_int]

        output_lines.append(f'\nNewly Listed Coins ({start_date} to {end_date}):')

        if new_listings:

            for (i, coin) in enumerate(new_listings, 1):

                output_lines.append(f"{i}. {coin['name']} ({coin['market']}): Listed on {coin['listing_date']}")

        else:

            output_lines.append('No new listings found in the specified date range.')

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_realtime_market_data(symbols: List[str], source: str, fields:Optional[List[str]], market: Optional[str]) -> str:

    '''```python
    """
    Fetch real-time market data snapshots for specified symbols.

    This function retrieves up-to-the-moment market data for a list of specified symbols, which can
    include equities, indices, or category tickers. The data is sourced from a specified provider and
    is intended for use in downstream analytics, such as sales or popularity trend modeling.

    Args:
        symbols (List[str]): A list of stock symbols, indices, or category tickers to fetch data for. Extract the symbols from the exact text description of the task in all capital letters.
        source (str): The data source provider, such as 'yahoo', 'bloomberg', 'alpha_vantage', or 'custom_api'.
            This is used to construct the data storage link and identify the data origin, should be in lowercase.
        fields (List[str], optional): A list of specific fields to retrieve from the market data. If not provided,
            defaults to ['symbol', 'name', 'last', 'change', 'change_pct', 'volume', 'turnover', 'market_cap', 'timestamp'].
            Available fields include:
            - 'symbol': Stock symbol/ticker
            - 'name': Company name
            - 'last': Last traded price
            - 'change': Price change from previous close
            - 'change_pct': Percentage change
            - 'volume': Trading volume
            - 'turnover': Total turnover value
            - 'market_cap': Market capitalization
            - 'timestamp': Data timestamp
            - 'category': Industry category
        market (str): The market or exchange identifier, such as 'NYSE', 'NASDAQ', 'SSE', or 'SZSE'.
            This is used in constructing the data storage link. It's not the city name.

    Returns:
        str: A URL linking to the data storage location where the fetched market data is stored.
            The link is constructed using the input parameters 'source' and 'market', formatted as:
            'https://{source}.marketdata.local/{market}/data'.

    Note:
        This function is designed to provide the freshest market numbers for analytics purposes and
        does not perform any data analysis or insight computation itself.
    """
```'''

    mock_market_snapshots = {('LIQUOR_CAT', 'yahoo'): {'symbol': 'LIQUOR_CAT', 'name': 'Liquor Industry Category Index', 'last': 3250.75, 'change': 15.2, 'change_pct': 0.47, 'volume': 4520000, 'turnover': 520000000.0, 'market_cap': None, 'timestamp': '2024-06-11T14:30:00+08:00', 'category': 'Liquor', 'source': 'yahoo', 'market': 'SSE'}, ('LIQUOR_CAT', 'xueqiu'): {'symbol': 'LIQUOR_CAT', 'name': '白酒行业指数', 'last': 3280.5, 'change': 18.75, 'change_pct': 0.57, 'volume': 4800000, 'turnover': 550000000.0, 'market_cap': None, 'timestamp': '2024-06-11T14:30:00+08:00', 'category': 'Liquor', 'source': 'xueqiu', 'market': 'CN'}, ('BANK_CAT', 'bloomberg'): {'symbol': 'BANK_CAT', 'name': 'Banking Industry Category Index', 'last': 980.2, 'change': -5.8, 'change_pct': -0.59, 'volume': 12800000, 'turnover': 1080000000.0, 'market_cap': None, 'timestamp': '2024-06-11T14:30:00+08:00', 'category': 'Banking', 'source': 'bloomberg', 'market': 'SZSE'}, ('BANK_CAT', 'xueqiu'): {'symbol': 'BANK_CAT', 'name': '银行行业指数', 'last': 975.8, 'change': -8.2, 'change_pct': -0.83, 'volume': 13500000, 'turnover': 1120000000.0, 'market_cap': None, 'timestamp': '2024-06-11T14:30:00+08:00', 'category': 'Banking', 'source': 'xueqiu', 'market': 'CN'}}

    if not isinstance(symbols, list) or not symbols:

        raise ValueError("Parameter 'symbols' must be a non-empty list of symbol strings.")

    if source is not None and (not isinstance(source, str)):

        raise ValueError("Parameter 'source' must be a string if provided.")

    if fields is not None and (not isinstance(fields, list) or not all((isinstance(f, str) for f in fields))):

        raise ValueError("Parameter 'fields' must be a list of strings if provided.")

    if market is not None and (not isinstance(market, str)):

        raise ValueError("Parameter 'market' must be a string if provided.")

    default_fields = ['symbol', 'name', 'last', 'change', 'change_pct', 'volume', 'turnover', 'market_cap', 'timestamp']

    fetched_data = {}

    for sym in symbols:

        snapshot = mock_market_snapshots.get((sym, source))

        if not snapshot:

            fetched_data[sym] = {'error': f'Symbol {sym} not found in {source} mock data.'}

            continue

        field_list = fields if fields else default_fields

        filtered_snapshot = {k: snapshot.get(k) for k in field_list if k in snapshot}

        filtered_snapshot['data_source'] = source

        filtered_snapshot['market'] = market

        fetched_data[sym] = filtered_snapshot

    import json

    mock_storage = {}

    mock_storage[f'{source}_{market}'] = fetched_data

    return f'https://{source}.marketdata.local/{market}_latest_snapshot.json'
@mcp.tool()
@safe_tool
def search_stock_byname(name: str) -> str:

    '''```python
    """
    Searches for stocks by name and returns a structured list of matching instruments.

    This function helps analysts quickly identify the correct stock by providing key
    identifiers and metadata for each result. Typical return fields include the company
    name, ticker symbol, and relevance score. This allows analysts to efficiently
    proceed with requesting quotes, histories, or comprehensive analysis reports.

    Args:
        name (str): The name or ticker symbol of the stock to search for. This should
            be a non-empty string.

    Returns:
        str: A formatted string containing a list of matching stocks with their company
        name, ticker symbol, and relevance score. If no matches are found, a message
        indicating no results will be returned.
    """
```'''

    mock_stock_db = [{'company_name': 'Alibaba Group Holding Limited', 'ticker': 'BABA', 'market': 'China', 'relevance_score': 0.95}, {'company_name': 'Tencent Holdings Limited', 'ticker': '0700.HK', 'market': 'China', 'relevance_score': 0.93}, {'company_name': 'JD.com, Inc.', 'ticker': 'JD', 'market': 'China', 'relevance_score': 0.9}, {'company_name': 'Meituan', 'ticker': '3690.HK', 'market': 'China', 'relevance_score': 0.88}, {'company_name': 'Pinduoduo Inc.', 'ticker': 'PDD', 'market': 'China', 'relevance_score': 0.87}, {'company_name': 'Apple Inc.', 'ticker': 'AAPL', 'market': 'US', 'relevance_score': 0.98}, {'company_name': 'Microsoft Corporation', 'ticker': 'MSFT', 'market': 'US', 'relevance_score': 0.97}, {'company_name': 'Alphabet Inc.', 'ticker': 'GOOGL', 'market': 'US', 'relevance_score': 0.96}, {'company_name': 'Tesla, Inc.', 'ticker': 'TSLA', 'market': 'US', 'relevance_score': 0.95}, {'company_name': 'NVIDIA Corporation', 'ticker': 'NVDA', 'market': 'US', 'relevance_score': 0.94}]

    if not isinstance(name, str) or not name.strip():

        return "Error: 'name' must be a non-empty string."

    name_lower = name.lower().strip()

    results = []

    for stock in mock_stock_db:

        if name_lower in stock['company_name'].lower() or name_lower in stock['ticker'].lower():

            results.append(stock)

    results.sort(key=lambda x: x['relevance_score'], reverse=True)

    results = results[:5]

    if not results:

        return f"No stocks found matching name '{name}'."

    output_lines = ['Search Results:']

    for r in results:

        output_lines.append(f"Company: {r['company_name']}, Ticker: {r['ticker']}, Relevance Score: {r['relevance_score']:.2f}")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_stock_news(ticker: str, max_result: int) -> str:

    '''```python
    """
    Retrieve the latest financial news articles related to a specific stock symbol or ticker.

    This function fetches and returns headlines, sources, publication dates, and article summaries
    for a given stock ticker. It helps users connect recent market movements with relevant news coverage.

    Args:
        ticker (str): The stock symbol or ticker for which to retrieve news articles. Must be a non-empty string.
            Valid tickers include: 'AAPL' (Apple Inc.), 'SSEC' (Shanghai Stock Exchange Composite Index),
            'SZCOMP' (Shenzhen Component Index). use the simple ticker codes.
        max_result (int): The maximum number of news articles to retrieve. Must be a positive integer. Defaults to 10 if not provided.

    Returns:
        str: A formatted string containing the latest news articles for the specified ticker, including headlines,
        sources, publication dates, and summaries. If no articles are found or if input validation fails, an error message is returned.
    """
```'''

    mock_news_db = {'AAPL': [{'headline': 'Apple Unveils New AI Features for iOS', 'source': 'TechCrunch', 'date': '2024-06-03', 'summary': 'Apple announced a range of AI-powered functionalities for its mobile operating system, aimed at boosting productivity.'}, {'headline': 'Apple Stock Rises Ahead of WWDC', 'source': 'Bloomberg', 'date': '2024-06-02', 'summary': 'Investors show optimism as Apple prepares to reveal new hardware and software updates.'}], 'SSEC': [{'headline': 'Shanghai Composite Rallies on Stimulus Hopes', 'source': 'Reuters', 'date': '2024-06-03', 'summary': 'The index surged over 2% as traders anticipated new government measures to boost the economy.'}, {'headline': 'Tech Stocks Lead Gains in Shanghai', 'source': 'Caixin', 'date': '2024-06-02', 'summary': 'Technology and consumer sectors drove the index higher amid positive earnings reports.'}], 'SZCOMP': [{'headline': 'Shenzhen Component Climbs on Manufacturing Data', 'source': 'South China Morning Post', 'date': '2024-06-03', 'summary': "Latest PMI data showed expansion in China's manufacturing sector, driving investor optimism."}, {'headline': 'New Energy Stocks Power Shenzhen Index', 'source': 'China Daily', 'date': '2024-06-01', 'summary': 'The surge in electric vehicle and battery firms boosted the overall index performance.'}]}

    if not isinstance(ticker, str) or not ticker.strip():

        return "Error: 'ticker' must be a non-empty string."

    if max_result is not None and (not isinstance(max_result, int) or max_result <= 0):

        return "Error: 'max_result' must be a positive integer if provided."

    if max_result is None:

        max_result = 10

    ticker_upper = ticker.strip().upper()

    if ticker_upper not in mock_news_db:

        return f"No news articles found for ticker '{ticker_upper}'."

    articles = mock_news_db[ticker_upper][:max_result]

    output_lines = [f'Latest news for {ticker_upper}:']

    for (i, article) in enumerate(articles, start=1):

        output_lines.append(f"{i}. {article['headline']} ({article['source']}, {article['date']})\n   Summary: {article['summary']}")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_markets(exchange: str) -> str:

    '''```python
    """
    Retrieve a list of all market codes supported by Upbit for trading.

    Args:
        exchange (str): The name of the exchange to query. If None, defaults to 'Upbit'.

    Returns:
        str: A formatted string listing all supported markets for the specified exchange,
             including details such as base currency, quote currency, popularity, and
             whether it is a new listing. Returns an error message if the exchange is
             not a string or is not found in the supported data.
    """
```'''

    mock_market_data = {'Upbit': [{'market': 'KRW-BTC', 'base_currency': 'BTC', 'quote_currency': 'KRW', 'status': 'active', 'popularity': 'high', 'new_listing': False}, {'market': 'KRW-ETH', 'base_currency': 'ETH', 'quote_currency': 'KRW', 'status': 'active', 'popularity': 'high', 'new_listing': False}, {'market': 'KRW-XRP', 'base_currency': 'XRP', 'quote_currency': 'KRW', 'status': 'active', 'popularity': 'medium', 'new_listing': False}, {'market': 'KRW-APT', 'base_currency': 'APT', 'quote_currency': 'KRW', 'status': 'active', 'popularity': 'emerging', 'new_listing': True}, {'market': 'KRW-SAND', 'base_currency': 'SAND', 'quote_currency': 'KRW', 'status': 'active', 'popularity': 'medium', 'new_listing': True}, {'market': 'BTC-ETH', 'base_currency': 'ETH', 'quote_currency': 'BTC', 'status': 'active', 'popularity': 'high', 'new_listing': False}]}

    if exchange is not None:

        if not isinstance(exchange, str):

            return "Error: 'exchange' parameter must be a string."

        if exchange not in mock_market_data:

            return f"Error: Exchange '{exchange}' not found in supported mock data."

    selected_exchange = exchange if exchange else 'Upbit'

    markets = mock_market_data[selected_exchange]

    output_lines = [f'Supported markets for {selected_exchange}:']

    for m in markets:

        new_tag = ' (New Listing)' if m['new_listing'] else ''

        output_lines.append(f"- {m['market']} | Base: {m['base_currency']}, Quote: {m['quote_currency']}, Popularity: {m['popularity']}{new_tag}")

    return '\n'.join(output_lines)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

