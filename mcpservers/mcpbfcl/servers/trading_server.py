"""
BFCL Trading MCP Server.
Wraps the TradingBot class as MCP tools for the BFCL benchmark.
"""
import json
from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.trading_bot import TradingBot
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-trading")
_instance = TradingBot()
@mcp.tool()
@safe_tool
def add_to_watchlist(stock: str) -> Dict[str, List[str]]:

    """
    Add a stock to the watchlist.

    Args:
        stock (str): the stock symbol to add to the watchlist.

    Returns:
        watchlist (List[str]): the watchlist.
    """

    return _instance.add_to_watchlist(stock=stock)
@mcp.tool()
@safe_tool
def cancel_order(order_id: int) -> Dict[str, Union[int, str]]:

    """
    Cancel an order.

    Args:
        order_id (int): ID of the order to cancel.

    Returns:
        order_id (int): ID of the cancelled order.
        status (str): New status of the order after cancellation attempt.
    """

    return _instance.cancel_order(order_id=order_id)
@mcp.tool()
@safe_tool
def filter_stocks_by_price(

    stocks: List[str], min_price: float, max_price: float
) -> Dict[str, List[str]]:

    """
    Filter stocks based on a price range.

    Args:
        stocks (List[str]): List of stock symbols to filter.
        min_price (float): Minimum stock price.
        max_price (float): Maximum stock price.

    Returns:
        filtered_stocks (List[str]): Filtered list of stock symbols within the price range.
    """

    return _instance.filter_stocks_by_price(

        stocks=stocks, min_price=min_price, max_price=max_price

    )
@mcp.tool()
@safe_tool
def fund_account(amount: float) -> Dict[str, Union[str, float]]:

    """
    Fund the account with the specified amount.

    Args:
        amount (float): Amount to fund the account with.

    Returns:
        status (str): Status of the funding operation.
        new_balance (float): Updated account balance after funding.
    """

    return _instance.fund_account(amount=amount)
@mcp.tool()
@safe_tool
def get_account_info() -> Dict[str, Union[int, float]]:

    """
    Get account information.

    Returns:
        account_id (int): ID of the account.
        balance (float): Current balance of the account.
        binding_card (int): Card number associated with the account.
    """

    return _instance.get_account_info()
@mcp.tool()
@safe_tool
def get_available_stocks(sector: str) -> Dict[str, List[str]]:

    """
    Get a list of stock symbols in the given sector.

    Args:
        sector (str): The sector to retrieve stocks from (e.g., 'Technology').

    Returns:
        stock_list (List[str]): List of stock symbols in the specified sector.
    """

    return _instance.get_available_stocks(sector=sector)
@mcp.tool()
@safe_tool
def get_current_time() -> Dict[str, str]:

    """
    Get the current time.

    Returns:
        current_time (str): Current time in HH:MM AM/PM format.
    """

    return _instance.get_current_time()
@mcp.tool()
@safe_tool
def get_order_details(order_id: int) -> Dict[str, Union[str, float, int]]:

    """
    Get the details of an order.

    Args:
        order_id (int): ID of the order.

    Returns:
        id (int): ID of the order.
        order_type (str): Type of the order.
        symbol (str): Symbol of the stock in the order.
        price (float): Price at which the order was placed.
        amount (int): Number of shares in the order.
        status (str): Current status of the order. [Enum]: ["Open", "Pending", "Completed", "Cancelled"]
    """

    return _instance.get_order_details(order_id=order_id)
@mcp.tool()
@safe_tool
def get_order_history() -> Dict[str, List[Dict[str, Union[str, int, float]]]]:

    """
    Get the stock order ID history.

    Returns:
        order_history (List[int]): List of orders ID in the order history.
    """

    return _instance.get_order_history()
@mcp.tool()
@safe_tool
def get_stock_info(symbol: str) -> Dict[str, Union[float, int, str]]:

    """
    Get the details of a stock.

    Args:
        symbol (str): Symbol that uniquely identifies the stock.

    Returns:
        price (float): Current price of the stock.
        percent_change (float): Percentage change in stock price.
        volume (float): Trading volume of the stock.
        MA(5) (float): 5-day Moving Average of the stock.
        MA(20) (float): 20-day Moving Average of the stock.
    """

    return _instance.get_stock_info(symbol=symbol)
@mcp.tool()
@safe_tool
def get_symbol_by_name(name: str) -> Dict[str, str]:

    """
    Get the symbol of a stock by company name.

    Args:
        name (str): Name of the company.

    Returns:
        symbol (str): Symbol of the stock or "Stock not found" if not available.
    """

    return _instance.get_symbol_by_name(name=name)
@mcp.tool()
@safe_tool
def get_transaction_history(

    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, List[Dict[str, Union[str, float]]]]:

    """
    Get the transaction history within a specified date range.

    Args:
        start_date (str): [Optional] Start date for the history (format: 'YYYY-MM-DD').
        end_date (str): [Optional] End date for the history (format: 'YYYY-MM-DD').

    Returns:
        transaction_history (List[Dict]): List of transactions within the specified date range.
            - type (str): Type of transaction. [Enum]: ["deposit", "withdrawal"]
            - amount (float): Amount involved in the transaction.
            - timestamp (str): Timestamp of the transaction, formatted as 'YYYY-MM-DD HH:MM:SS'.
    """

    return _instance.get_transaction_history(start_date=start_date, end_date=end_date)
@mcp.tool()
@safe_tool
def get_watchlist() -> Dict[str, List[str]]:

    """
    Get the watchlist.

    Returns:
        watchlist (List[str]): List of stock symbols in the watchlist.
    """

    return _instance.get_watchlist()
@mcp.tool()
@safe_tool
def notify_price_change(stocks: List[str], threshold: float) -> Dict[str, str]:

    """
    Notify if there is a significant price change in the stocks.

    Args:
        stocks (List[str]): List of stock symbols to check.
        threshold (float): Percentage change threshold to trigger a notification.

    Returns:
        notification (str): Notification message about the price changes.
    """

    return _instance.notify_price_change(stocks=stocks, threshold=threshold)
@mcp.tool()
@safe_tool
def place_order(

    order_type: str, symbol: str, price: float, amount: int
) -> Dict[str, Union[int, str, float]]:

    """
    Place an order.

    Args:
        order_type (str): Type of the order (Buy/Sell).
        symbol (str): Symbol of the stock to trade.
        price (float): Price at which to place the order.
        amount (int): Number of shares to trade.

    Returns:
        order_id (int): ID of the newly placed order.
        order_type (str): Type of the order (Buy/Sell).
        status (str): Initial status of the order.
        price (float): Price at which the order was placed.
        amount (int): Number of shares in the order.
    """

    return _instance.place_order(

        order_type=order_type, symbol=symbol, price=price, amount=amount

    )
@mcp.tool()
@safe_tool
def remove_stock_from_watchlist(symbol: str) -> Dict[str, str]:

    """
    Remove a stock from the watchlist.

    Args:
        symbol (str): Symbol of the stock to remove.

    Returns:
        status (str): Status of the removal operation.
    """

    return _instance.remove_stock_from_watchlist(symbol=symbol)
@mcp.tool()
@safe_tool
def trading_get_login_status() -> Dict[str, bool]:

    """
    Get the login status.

    Returns:
        status (bool): Login status.
    """

    return _instance.trading_get_login_status()
@mcp.tool()
@safe_tool
def trading_login(username: str, password: str) -> Dict[str, str]:

    """
    Handle user login.

    Args:
        username (str): Username for authentication.
        password (str): Password for authentication.

    Returns:
        status (str): Login status message.
    """

    return _instance.trading_login(username=username, password=password)
@mcp.tool()
@safe_tool
def trading_logout() -> Dict[str, str]:

    """
    Handle user logout for trading system.

    Returns:
        status (str): Logout status message.
    """

    return _instance.trading_logout()
@mcp.tool()
@safe_tool
def withdraw_funds(amount: float) -> Dict[str, Union[str, float]]:

    """
    Withdraw funds from the account balance.

    Args:
        amount (float): Amount to withdraw from the account.

    Returns:
        status (str): Status of the transaction.
        new_balance (float): Updated account balance after the transaction.
    """

    return _instance.withdraw_funds(amount=amount)
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """
    Load a scenario configuration into the trading system.

    Args:
        config_json (str): JSON string containing the scenario configuration.
        long_context (bool): If True, extend state with long-context data.

    Returns:
        str: "OK" on success.
    """

    _instance._load_scenario(json.loads(config_json), long_context=long_context)

    return "OK"
@mcp.tool()
def admin_get_state() -> str:

    """
    Get the current state of the trading system.

    Returns:
        str: JSON string of the current public state.
    """

    return json.dumps(

        {attr: val for attr, val in vars(_instance).items() if not attr.startswith("_")},

        default=str,

    )
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

