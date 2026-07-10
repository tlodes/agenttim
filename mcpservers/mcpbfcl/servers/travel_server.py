"""
BFCL Travel MCP Server.
Wraps the TravelAPI class as MCP tools for the BFCL benchmark.
"""
import json
from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.travel_booking import TravelAPI
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-travel")
_instance = TravelAPI()
@mcp.tool()
@safe_tool
def authenticate_travel(

    client_id: str,

    client_secret: str,

    refresh_token: str,

    grant_type: str,

    user_first_name: str,

    user_last_name: str,
) -> Dict[str, Union[int, str]]:

    """
    Authenticate the user with the travel API

    Args:
        client_id (str): The client applications client_id supplied by App Management
        client_secret (str): The client applications client_secret supplied by App Management
        refresh_token (str): The refresh token obtained from the initial authentication
        grant_type (str): The grant type of the authentication request. Here are the options: read_write, read, write
        user_first_name (str): The first name of the user
        user_last_name (str): The last name of the user
    Returns:
        expires_in (int): The number of time it can use until the access token expires
        access_token (str): The access token to be used in the Authorization header of future requests
        token_type (str): The type of token
        scope (str): The scope of the token
    """

    return _instance.authenticate_travel(

        client_id=client_id,

        client_secret=client_secret,

        refresh_token=refresh_token,

        grant_type=grant_type,

        user_first_name=user_first_name,

        user_last_name=user_last_name,

    )
@mcp.tool()
@safe_tool
def book_flight(

    access_token: str,

    card_id: str,

    travel_date: str,

    travel_from: str,

    travel_to: str,

    travel_class: str,
) -> Dict[str, Union[str, bool, Dict]]:

    """
    Book a flight given the travel information. From and To should be the airport codes in the IATA format.

    Args:
        access_token (str): The access token obtained from the authenticate
        card_id (str): The ID of the credit card to use for the booking
        travel_date (str): The date of the travel in the format YYYY-MM-DD
        travel_from (str): The location the travel is from
        travel_to (str): The location the travel is to
        travel_class (str): The class of the travel
    Returns:
        booking_id (str): The ID of the booking
        transaction_id (str): The ID of the transaction
        booking_status (bool): The status of the booking, True if successful, False if failed
        booking_history (Dict): The booking history. This field might be empty even though the history is non-empty.
    """

    return _instance.book_flight(

        access_token=access_token,

        card_id=card_id,

        travel_date=travel_date,

        travel_from=travel_from,

        travel_to=travel_to,

        travel_class=travel_class,

    )
@mcp.tool()
@safe_tool
def cancel_booking(

    access_token: str, booking_id: str
) -> Dict[str, Union[bool, str]]:

    """
    Cancel a booking

    Args:
        access_token (str): The access token obtained from the authenticate
        booking_id (str): The ID of the booking
    Returns:
        cancel_status (bool): The status of the cancellation, True if successful, False if failed
    """

    return _instance.cancel_booking(access_token=access_token, booking_id=booking_id)
@mcp.tool()
@safe_tool
def compute_exchange_rate(

    base_currency: str, target_currency: str, value: float
) -> float:

    """
    Compute the exchange rate between two currencies

    Args:
        base_currency (str): The base currency. [Enum]: USD, RMB, EUR, JPY, GBP, CAD, AUD, INR, RUB, BRL, MXN
        target_currency (str): The target currency. [Enum]: USD, RMB, EUR, JPY, GBP, CAD, AUD, INR, RUB, BRL, MXN
        value (float): The value to convert
    Returns:
        exchanged_value (float): The value after the exchange
    """

    return _instance.compute_exchange_rate(

        base_currency=base_currency, target_currency=target_currency, value=value

    )
@mcp.tool()
@safe_tool
def contact_customer_support(booking_id: str, message: str) -> Dict[str, str]:

    """
    Contact travel booking customer support, get immediate support on an issue with an online call.

    Args:
        booking_id (str): The ID of the booking
        message (str): The message to send to customer support
    Returns:
        customer_support_message (str): The message from customer support
    """

    return _instance.contact_customer_support(booking_id=booking_id, message=message)
@mcp.tool()
@safe_tool
def get_all_credit_cards() -> Dict[str, Dict[str, Union[str, int, float]]]:

    """
    Get all registered credit cards

    Returns:
        credit_card_list (Dict): A dictionary containing all registered credit cards
            - card_number (str): The number of the credit card
            - expiration_date (str): The expiration date of the credit card in the format YYYY-MM-DD
            - cardholder_name (str): The name of the cardholder
            - card_verification_value (int): The verification value of the credit card
            - balance (float): The balance of the credit card
    """

    return _instance.get_all_credit_cards()
@mcp.tool()
@safe_tool
def get_booking_history(

    access_token: str,
) -> Dict[str, Dict[str, Dict[str, Union[str, float]]]]:

    """
    Retrieve all booking history for the user.

    Args:
        access_token (str): The access token obtained from the authenticate method.

    Returns:
        booking_history (Dict): A dictionary keyed by booking_id where each value contains the booking details.
            - transaction_id (str): The ID of the transaction
            - travel_date (str): The date of the travel
            - travel_from (str): The location the travel is from
            - travel_to (str): The location the travel is to
            - travel_class (str): The class of the travel
            - travel_cost (float): The cost of the travel
    """

    return _instance.get_booking_history(access_token=access_token)
@mcp.tool()
@safe_tool
def get_budget_fiscal_year(

    lastModifiedAfter: Optional[str] = None,

    includeRemoved: Optional[str] = None,
) -> Dict[str, str]:

    """
    Get the budget fiscal year

    Args:
        lastModifiedAfter (str): [Optional] Use this field if you only want Fiscal Years that were changed after the supplied date. The supplied date will be interpreted in the UTC time zone. If lastModifiedAfter is not supplied, the service will return all Fiscal Years, regardless of modified date. Example: 2016-03-29T16:12:20. Return in the format of YYYY-MM-DDTHH:MM:SS.
        includeRemoved (str): [Optional] If true, the service will return all Fiscal Years, including those that were previously removed. If not supplied, this field defaults to false.
    Returns:
        budget_fiscal_year (str): The budget fiscal year
    """

    return _instance.get_budget_fiscal_year(

        lastModifiedAfter=lastModifiedAfter, includeRemoved=includeRemoved

    )
@mcp.tool()
@safe_tool
def get_credit_card_balance(

    access_token: str, card_id: str
) -> Dict[str, Union[float, str]]:

    """
    Get the balance of a credit card

    Args:
        access_token (str): The access token obtained from the authenticate
        card_id (str): The ID of the credit card
    Returns:
        card_balance (float): The balance of the credit card
    """

    return _instance.get_credit_card_balance(access_token=access_token, card_id=card_id)
@mcp.tool()
@safe_tool
def get_flight_cost(

    travel_from: str, travel_to: str, travel_date: str, travel_class: str
) -> Dict[str, List[float]]:

    """
    Get the list of cost of a flight in USD based on location, date, and class

    Args:
        travel_from (str): The 3 letter code of the departing airport
        travel_to (str): The 3 letter code of the arriving airport
        travel_date (str): The date of the travel in the format 'YYYY-MM-DD'
        travel_class (str): The class of the travel. Options are: economy, business, first.
    Returns:
        travel_cost_list (List[float]): The list of cost of the travel
    """

    return _instance.get_flight_cost(

        travel_from=travel_from,

        travel_to=travel_to,

        travel_date=travel_date,

        travel_class=travel_class,

    )
@mcp.tool()
@safe_tool
def get_nearest_airport_by_city(location: str) -> Dict[str, str]:

    """
    Get the nearest airport to the given location

    Args:
        location (str): The name of the location. [Enum]: Rivermist, Stonebrook, Maplecrest, Silverpine, Shadowridge, London, Paris, Sunset Valley, Oakendale, Willowbend, Crescent Hollow, Autumnville, Pinehaven, Greenfield, San Francisco, Los Angeles, New York, Chicago, Boston, Beijing, Hong Kong, Rome, Tokyo
    Returns:
        nearest_airport (str): The nearest airport to the given location
    """

    return _instance.get_nearest_airport_by_city(location=location)
@mcp.tool()
@safe_tool
def list_all_airports() -> List[str]:

    """
    List all available airports

    Returns:
        airports (List[str]): A list of all available airports
    """

    return _instance.list_all_airports()
@mcp.tool()
@safe_tool
def purchase_insurance(

    access_token: str,

    insurance_type: str,

    booking_id: str,

    insurance_cost: float,

    card_id: str,
) -> Dict[str, Union[str, bool]]:

    """
    Purchase insurance

    Args:
        access_token (str): The access token obtained from the authenticate
        insurance_type (str): The type of insurance to purchase
        insurance_cost (float): The cost of the insurance
        booking_id (str): The ID of the booking
        card_id (str): The ID of the credit card to use for the
    Returns:
        insurance_id (str): The ID of the insurance
        insurance_status (bool): The status of the insurance purchase, True if successful, False if failed
    """

    return _instance.purchase_insurance(

        access_token=access_token,

        insurance_type=insurance_type,

        booking_id=booking_id,

        insurance_cost=insurance_cost,

        card_id=card_id,

    )
@mcp.tool()
@safe_tool
def register_credit_card(

    access_token: str,

    card_number: str,

    expiration_date: str,

    cardholder_name: str,

    card_verification_number: int,
) -> Dict[str, Union[str, Dict[str, str]]]:

    """
    Register a credit card

    Args:
        access_token (str): The access token obtained from the authenticate method
        card_number (str): The credit card number
        expiration_date (str): The expiration date of the credit card in the format MM/YYYY
        cardholder_name (str): The name of the cardholder
        card_verification_number (int): The card verification number
    Returns:
        card_id (str): The ID of the registered credit card
    """

    return _instance.register_credit_card(

        access_token=access_token,

        card_number=card_number,

        expiration_date=expiration_date,

        cardholder_name=cardholder_name,

        card_verification_number=card_verification_number,

    )
@mcp.tool()
@safe_tool
def retrieve_invoice(

    access_token: str,

    booking_id: Optional[str] = None,

    insurance_id: Optional[str] = None,
) -> Dict[str, Union[Dict[str, Union[str, float]], str]]:

    """
    Retrieve the invoice for a booking.

    Args:
        access_token (str): The access token obtained from the authenticate
        booking_id (str): [Optional] The ID of the booking
        insurance_id (str): [Optional] The ID of the insurance
    Returns:
        invoice (Dict): The invoice for the booking
            - booking_id (str): The ID of the booking
            - travel_date (str): The date of the travel
            - travel_from (str): The location the travel is from
            - travel_to (str): The location the travel is to
            - travel_class (str): The class of the travel
            - travel_cost (float): The cost of the travel
            - transaction_id (str): The ID of the transaction
    """

    return _instance.retrieve_invoice(

        access_token=access_token, booking_id=booking_id, insurance_id=insurance_id

    )
@mcp.tool()
@safe_tool
def set_budget_limit(

    access_token: str, budget_limit: float
) -> Dict[str, Union[float, str]]:

    """
    Set the budget limit for the user

    Args:
        access_token (str): The access token obtained from the authentication process or initial configuration.
        budget_limit (float): The budget limit to set in USD
    Returns:
        budget_limit (float): The budget limit set in USD
    """

    return _instance.set_budget_limit(access_token=access_token, budget_limit=budget_limit)
@mcp.tool()
@safe_tool
def travel_get_login_status() -> Dict[str, bool]:

    """
    Get the status of the login

    Returns:
        status (bool): The status of the login
    """

    return _instance.travel_get_login_status()
@mcp.tool()
@safe_tool
def verify_traveler_information(

    first_name: str, last_name: str, date_of_birth: str, passport_number: str
) -> Dict[str, Union[bool, str]]:

    """
    Verify the traveler information

    Args:
        first_name (str): The first name of the traveler
        last_name (str): The last name of the traveler
        date_of_birth (str): The date of birth of the traveler in the format YYYY-MM-DD
        passport_number (str): The passport number of the traveler
    Returns:
        verification_status (bool): The status of the verification, True if successful, False if failed
        verification_failure (str): The reason for the verification failure
    """

    return _instance.verify_traveler_information(

        first_name=first_name,

        last_name=last_name,

        date_of_birth=date_of_birth,

        passport_number=passport_number,

    )
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """
    Load a scenario configuration into the travel system.

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
    Get the current state of the travel system.

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

