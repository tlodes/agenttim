"""
Domain configuration for BFCL (Berkeley Function Calling Leaderboard) evaluation.
Maps 128 tools across 8 API domains. Each BFCL class corresponds to one domain
with semantically related tools that share state and operate on the same API.
"""
CLASS_TO_MODULE: dict[str, str] = {

    "GorillaFileSystem": "gorilla_file_system",

    "MathAPI": "math_api",

    "MessageAPI": "message_api",

    "TwitterAPI": "posting_api",

    "TicketAPI": "ticket_api",

    "TradingBot": "trading_bot",

    "TravelAPI": "travel_booking",

    "VehicleControlAPI": "vehicle_control",
}
CLASS_TO_DOMAIN: dict[str, str] = {

    "GorillaFileSystem": "filesystem",

    "MathAPI": "math",

    "MessageAPI": "messaging",

    "TwitterAPI": "social",

    "TicketAPI": "ticketing",

    "TradingBot": "trading",

    "TravelAPI": "travel",

    "VehicleControlAPI": "vehicle",
}
DOMAIN_TOOLS: dict[str, list[str]] = {

    "filesystem": [

        "cat",

        "cd",

        "cp",

        "diff",

        "du",

        "echo",

        "find",

        "grep",

        "ls",

        "mkdir",

        "mv",

        "pwd",

        "rm",

        "rmdir",

        "sort",

        "tail",

        "touch",

        "wc",

    ],

    "math": [

        "absolute_value",

        "add",

        "divide",

        "imperial_si_conversion",

        "logarithm",

        "max_value",

        "mean",

        "min_value",

        "multiply",

        "percentage",

        "power",

        "round_number",

        "si_unit_conversion",

        "square_root",

        "standard_deviation",

        "subtract",

        "sum_values",

    ],

    "messaging": [

        "add_contact",

        "delete_message",

        "get_message_stats",

        "get_user_id",

        "list_users",

        "message_get_login_status",

        "message_login",

        "search_messages",

        "send_message",

        "view_messages_sent",

    ],

    "social": [

        "authenticate_twitter",

        "comment",

        "follow_user",

        "get_tweet",

        "get_tweet_comments",

        "get_user_stats",

        "get_user_tweets",

        "list_all_following",

        "mention",

        "post_tweet",

        "posting_get_login_status",

        "retweet",

        "search_tweets",

        "unfollow_user",

    ],

    "ticketing": [

        "close_ticket",

        "create_ticket",

        "edit_ticket",

        "get_ticket",

        "get_user_tickets",

        "logout",

        "resolve_ticket",

        "ticket_get_login_status",

        "ticket_login",

    ],

    "trading": [

        "add_to_watchlist",

        "cancel_order",

        "filter_stocks_by_price",

        "fund_account",

        "get_account_info",

        "get_available_stocks",

        "get_current_time",

        "get_order_details",

        "get_order_history",

        "get_stock_info",

        "get_symbol_by_name",

        "get_transaction_history",

        "get_watchlist",

        "notify_price_change",

        "place_order",

        "remove_stock_from_watchlist",

        "trading_get_login_status",

        "trading_login",

        "trading_logout",

        "withdraw_funds",

    ],

    "travel": [

        "authenticate_travel",

        "book_flight",

        "cancel_booking",

        "compute_exchange_rate",

        "contact_customer_support",

        "get_all_credit_cards",

        "get_booking_history",

        "get_budget_fiscal_year",

        "get_credit_card_balance",

        "get_flight_cost",

        "get_nearest_airport_by_city",

        "list_all_airports",

        "purchase_insurance",

        "register_credit_card",

        "retrieve_invoice",

        "set_budget_limit",

        "travel_get_login_status",

        "verify_traveler_information",

    ],

    "vehicle": [

        "activateParkingBrake",

        "adjustClimateControl",

        "check_tire_pressure",

        "displayCarStatus",

        "display_log",

        "estimate_distance",

        "estimate_drive_feasibility_by_mileage",

        "fillFuelTank",

        "find_nearest_tire_shop",

        "gallon_to_liter",

        "get_current_speed",

        "get_outside_temperature_from_google",

        "get_outside_temperature_from_weather_com",

        "get_zipcode_based_on_city",

        "liter_to_gallon",

        "lockDoors",

        "pressBrakePedal",

        "releaseBrakePedal",

        "setCruiseControl",

        "setHeadlights",

        "set_navigation",

        "startEngine",

    ],
}
DOMAIN_DESCRIPTIONS: dict[str, str] = {

    "filesystem": "File system operations: navigation, file creation, reading, writing, and search",

    "math": "Mathematical operations: arithmetic, statistics, unit conversion, and precision math",

    "messaging": "Workspace messaging: user management, sending/receiving messages, and contacts",

    "social": "Social media (Twitter-like): posting, retweeting, commenting, and following users",

    "ticketing": "Support ticket management: creation, resolution, editing, and status tracking",

    "trading": "Stock trading: order placement, account management, watchlists, and market data",

    "travel": "Travel booking: flights, credit cards, insurance, budgets, and airport lookup",

    "vehicle": "Vehicle control: engine, doors, climate, navigation, brakes, and diagnostics",
}
ALL_DOMAINS: list[str] = list(DOMAIN_TOOLS.keys())
COARSE_AGENT_GROUPS: dict[str, dict] = {

    "digital_services": {

        "description": "Digital interaction domains: filesystem, messaging, social media, and ticketing",

        "domains": ["filesystem", "messaging", "social", "ticketing"],

        "prompt": (

            "You are a Digital Services Assistant. You have tools for file system operations "

            "(ls, cat, grep, find, etc.), workspace messaging (send, search, contacts), "

            "social media (tweets, retweets, comments, following), and support tickets "

            "(create, resolve, close). Read tool descriptions carefully, pick the right one, "

            "and return results directly."

        ),

    },

    "commerce": {

        "description": "Commerce and travel domains: stock trading and travel booking",

        "domains": ["trading", "travel"],

        "prompt": (

            "You are a Commerce Assistant. You have tools for stock trading (place orders, "

            "manage watchlists, view account info, check stock prices) and travel booking "

            "(search flights, book flights, manage credit cards, purchase insurance, check "

            "budgets). Read tool descriptions carefully, pick the right one, and return "

            "results directly."

        ),

    },

    "physical": {

        "description": "Physical world domains: mathematical computation and vehicle control",

        "domains": ["math", "vehicle"],

        "prompt": (

            "You are a Physical World Assistant. You have tools for mathematical operations "

            "(arithmetic, statistics, unit conversions, logarithms) and vehicle control "

            "(engine start/stop, door locks, climate control, navigation, tire pressure, "

            "fuel management). Read tool descriptions carefully, pick the right one, and "

            "return results directly."

        ),

    },
}
def get_tool_to_domain_map() -> dict[str, str]:

    """Return a mapping from tool name to domain name."""

    result: dict[str, str] = {}

    for domain, tools in DOMAIN_TOOLS.items():

        for tool in tools:

            result[tool] = domain

    return result
BASE_PROMPT = """You are an expert in composing functions. You are given a question and a set of possible functions. Based on the question, you will need to make one or more function/tool calls to achieve the purpose. If none of the functions can be used, point it out. If the given question lacks the parameters required by the function, also point it out.
At each turn, you should try your best to complete the tasks requested by the user within the current turn. Continue to output functions to call until you have fulfilled the user's request to the best of your ability. Once you have no more functions to call, the system will consider the current turn complete and proceed to the next turn or task.
When working with file system operations, always use cd to navigate to the target directory first, then operate on files using their plain names — never use paths containing /. For example, to move a file inside 'documents/archive', first cd('documents'), then cd('archive'), then operate on the file."""
def get_domain_for_class(class_name: str) -> str:

    """Return the domain name for a given BFCL class name.

    Raises:
        KeyError: If the class name is not found in CLASS_TO_DOMAIN.
    """

    if class_name not in CLASS_TO_DOMAIN:

        raise KeyError(

            f"Unknown BFCL class '{class_name}'. "

            f"Known classes: {', '.join(CLASS_TO_DOMAIN.keys())}"

        )

    return CLASS_TO_DOMAIN[class_name]

