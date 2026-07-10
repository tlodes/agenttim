"""
MCPAgentBench Lifestyle MCP Server.
Concrete FastMCP server with 12 tools for the lifestyle domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from typing import Literal
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-lifestyle")
@mcp.tool()
@safe_tool
def package_delivery_tracker(tracking_number: str) -> str:

    '''"""
Provide the current status of a package by its tracking number.
The tool contains a small simulated carrier database with standardized status
codes. Each tracking number must exactly match one of the entries below. The
response includes the last known checkpoint, estimated delivery window, and the
carrier handling the shipment.
Args:
    tracking_number (str): Unique shipment identifier printed on the shipping label.
Returns:
    str: Status summary with location, timestamp, and ETA, or an error if unknown.
"""'''

    shipments = {

        '1Z999AA10123456784': {

            'carrier': 'UPS',

            'status': 'In Transit',

            'last_scan': 'Portland, OR Distribution Center',

            'timestamp': '10/31/2025 21:42',

            'eta': '11/02/2025',

        },

        '9400111899223951135987': {

            'carrier': 'USPS',

            'status': 'Out for Delivery',

            'last_scan': 'Seattle, WA Carrier Facility',

            'timestamp': '11/01/2025 07:15',

            'eta': '11/01/2025',

        },

        '786512345678': {

            'carrier': 'FedEx',

            'status': 'Delayed - Weather',

            'last_scan': 'Denver, CO Hub',

            'timestamp': '10/31/2025 18:05',

            'eta': '11/04/2025',

        },

        'JD000222333444555666': {

            'carrier': 'DHL',

            'status': 'Arrived at Destination Facility',

            'last_scan': 'Frankfurt, DE Gateway',

            'timestamp': '10/31/2025 12:50',

            'eta': '11/03/2025',

        },

    }

    if not tracking_number:

        return "Error: 'tracking_number' is required."

    record = shipments.get(tracking_number)

    if not record:

        return f"Error: Tracking number '{tracking_number}' not found."

    return (

        f"Carrier: {record['carrier']}\n"

        f"Status: {record['status']}\n"

        f"Last Scan: {record['last_scan']}\n"

        f"Timestamp: {record['timestamp']}\n"

        f"Estimated Delivery: {record['eta']}"

    )
@mcp.tool()
@safe_tool
def pay_utility_bill(account_number: str, provider: str, amount: float, method: Literal['online', 'in_person', 'auto_debit']='online') -> str:

    '''"""
Submit a payment request for a household utility bill.
Supports electricity, water, gas, and internet service providers stored in the mock
billing registry below. The `amount` must match a pending balance or the payment
will be rejected. This tool simulates a payment gateway and does not perform any
real transactions.
Args:
    account_number (str): Unique account identifier registered with the provider.
    provider (str): Utility provider name, case-insensitive (e.g., "Seattle Water").
    amount (float): Payment amount in USD. Must equal the pending balance on record.
    method (Literal['online', 'in_person', 'auto_debit']): Preferred payment channel.
Returns:
    str: Confirmation string when successful or a descriptive error message.
"""'''

    billing_registry = {

        'Seattle Power': {'A10293': {'balance': 84.71, 'due_date': '11/20/2025'}},

        'Seattle Water': {'W55821': {'balance': 42.18, 'due_date': '11/22/2025'}},

        'Metro Gas': {'G90110': {'balance': 67.44, 'due_date': '11/18/2025'}},

        'Northlink Internet': {'N77654': {'balance': 59.99, 'due_date': '11/25/2025'}},

        'Evergreen Solar': {'E44567': {'balance': 35.12, 'due_date': '11/28/2025'}},

    }

    normalized_provider = provider.strip().title() if provider else ''

    if not account_number:

        return "Error: 'account_number' is required."

    if not normalized_provider:

        return "Error: 'provider' is required."

    if normalized_provider not in billing_registry:

        return f"Error: Provider '{provider}' not recognized."

    provider_accounts = billing_registry[normalized_provider]

    if account_number not in provider_accounts:

        return f"Error: No record found for account '{account_number}'."

    account_record = provider_accounts[account_number]

    pending_balance = account_record['balance']

    if amount != pending_balance:

        return f"Error: Payment amount must match the pending balance of ${pending_balance:.2f}."

    if method not in ['online', 'in_person', 'auto_debit']:

        return "Error: Unsupported payment method."

    confirmation = (

        "Payment submitted successfully!\n"

        f"Provider: {normalized_provider}\n"

        f"Account: {account_number}\n"

        f"Amount: ${amount:.2f}\n"

        f"Due Date: {account_record['due_date']}\n"

        f"Method: {method}"

    )

    return confirmation
@mcp.tool()
@safe_tool
def public_transport_card_recharge(card_number: str, amount: float) -> str:

    '''"""
Apply a stored-value recharge to a public transit card.
Cards have maximum balances; recharges must keep the balance under $200. The tool
validates the amount and the card status before confirming the transaction.
Args:
    card_number (str): Transit authority card identifier.
    amount (float): Amount in USD to add. Must be between 5 and 100 inclusive, accurate to one decimal place.
Returns:
    str: Updated balance confirmation or an error message when validation fails.
"""'''

    cards = {

        'ORCA-551122': {'status': 'Active', 'balance': 42.75},

        'ORCA-773344': {'status': 'Active', 'balance': 180.00},

        'ORCA-889910': {'status': 'Suspended', 'balance': 15.25},

    }

    if not card_number:

        return "Error: 'card_number' is required."

    if amount <= 0:

        return "Error: Recharge amount must be positive."

    if amount < 5 or amount > 100:

        return "Error: Amount must be between $5 and $100."

    card = cards.get(card_number.upper())

    if not card:

        return f"Error: Card '{card_number}' not found."

    if card['status'] != 'Active':

        return f"Error: Card status is {card['status']}."

    new_balance = card['balance'] + amount

    if new_balance > 200:

        return "Error: Recharge would exceed maximum balance of $200."

    return (

        f"Recharge successful!\n"

        f"Card: {card_number}\n"

        f"Amount Added: ${amount:.2f}\n"

        f"New Balance: ${new_balance:.2f}"

    )
@mcp.tool()
@safe_tool
def laundry_service_request(customer_id: str, pickup_date: str, service_type: Literal['wash_fold', 'dry_cleaning', 'press_only']) -> str:

    '''"""
Submit a pickup request for a laundry service.
Pickup windows are validated against service availability. Different service
categories have separate turn-around times. All dates must use `YYYY-MM-DD`.
Args:
    customer_id (str): Registered customer identifier.
    pickup_date (str): Requested pickup date in `YYYY-MM-DD` format.
    service_type (Literal['wash_fold', 'dry_cleaning', 'press_only']): Desired service option.
Returns:
    str: Confirmation with drop-off estimate or an error message when unavailable.
"""'''

    availability = {

        'wash_fold': {'2025-11-01': True, '2025-11-03': True, '2025-11-05': False},

        'dry_cleaning': {'2025-11-01': False, '2025-11-02': True, '2025-11-04': True},

        'press_only': {'2025-11-02': True, '2025-11-03': True, '2025-11-06': True},

    }

    turnaround_hours = {'wash_fold': 24, 'dry_cleaning': 48, 'press_only': 12}

    if not customer_id:

        return "Error: 'customer_id' is required."

    if not pickup_date:

        return "Error: 'pickup_date' is required."

    if service_type not in availability:

        return "Error: Unsupported service type."

    service_calendar = availability[service_type]

    if pickup_date not in service_calendar or not service_calendar[pickup_date]:

        return f"Error: {service_type} is fully booked on {pickup_date}."

    return (

        f"Laundry pickup scheduled!\n"

        f"Customer: {customer_id}\n"

        f"Service: {service_type}\n"

        f"Pickup Date: {pickup_date}\n"

        f"Estimated Completion: {turnaround_hours[service_type]} hour(s) after pickup"

    )
@mcp.tool()
@safe_tool
def trash_collection_schedule(service_address: str, waste_type: str) -> str:

    '''"""
Retrieve the curbside pickup schedule for a specific waste stream.
Supported waste streams are `garbage`, `recycling`, and `compost`. Addresses are
indexed by route code in the mock database. The tool returns the next pickup day
and any holiday adjustments.
Args:
    service_address (str): Street address registered with the sanitation service.
    waste_type (str): Waste category to look up. One of `garbage`, `recycling`, `compost`.
Returns:
    str: Upcoming pickup window or an error message when the address is unknown.
"""'''

    routes = {

        '742 Evergreen Terrace': {

            'garbage': {'next_pickup': '11/04/2025', 'note': 'Set out by 7:00 AM'},

            'recycling': {'next_pickup': '11/07/2025', 'note': 'Blue bin only'},

            'compost': {'next_pickup': '11/04/2025', 'note': 'Holiday schedule - pickup delayed one day'},

        },

        '1234 Lakeview Drive': {

            'garbage': {'next_pickup': '11/02/2025', 'note': 'Normal service'},

            'recycling': {'next_pickup': '11/09/2025', 'note': 'Rinse containers'},

            'compost': {'next_pickup': '11/02/2025', 'note': 'Place cart 3 ft from bins'},

        },

        '501 Pine Street': {

            'garbage': {'next_pickup': '11/03/2025', 'note': 'Extra bag tags required'},

            'recycling': {'next_pickup': '11/10/2025', 'note': 'Flatten cardboard'},

            'compost': {'next_pickup': '11/03/2025', 'note': 'Remove produce stickers'},

        },

    }

    if not service_address:

        return "Error: 'service_address' is required."

    if waste_type not in ['garbage', 'recycling', 'compost']:

        return "Error: Unsupported waste type."

    record = routes.get(service_address)

    if not record:

        return f"Error: Address '{service_address}' not found."

    schedule = record[waste_type]

    return (

        f"Next Pickup: {schedule['next_pickup']}\n"

        f"Instructions: {schedule['note']}"

    )
@mcp.tool()
@safe_tool
def community_pool_pass_renewal(member_id: str, renewal_term: int) -> str:

    '''"""
Process a renewal for a community pool membership pass.
Memberships may be extended in 3, 6, or 12 month increments. The tool validates
member status, calculates the new expiration date, and reports the renewal fee.
Args:
    member_id (str): Unique pass identifier.
    renewal_term (int): Number of months to renew (3, 6, or 12).
Returns:
    str: Renewal confirmation with new expiration date and amount due.
"""'''

    members = {

        'PASS-3301': {'name': 'Jordan Lee', 'expiration': '2025-12-15', 'status': 'Active'},

        'PASS-4488': {'name': 'Priya Patel', 'expiration': '2025-11-20', 'status': 'Active'},

        'PASS-9921': {'name': 'Alex Gomez', 'expiration': '2025-10-01', 'status': 'Expired'},

    }

    pricing = {3: 45.00, 6: 80.00, 12: 150.00}

    if not member_id:

        return "Error: 'member_id' is required."

    if renewal_term not in pricing:

        return "Error: Renewal term must be 3, 6, or 12 months."

    record = members.get(member_id.upper())

    if not record:

        return f"Error: Member '{member_id}' not found."

    if record['status'] == 'Expired' and renewal_term < 6:

        return "Error: Expired memberships require at least a 6-month renewal."

    return (

        f"Renewal successful!\n"

        f"Member: {record['name']}\n"

        f"Current Expiration: {record['expiration']}\n"

        f"New Term: {renewal_term} month(s)\n"

        f"Amount Due: ${pricing[renewal_term]:.2f}"

    )
@mcp.tool()
@safe_tool
def home_appliance_warranty_lookup(serial_number: str) -> str:

    '''"""
Check warranty coverage and service phone numbers for major appliances.
Only serial numbers in the table below are recognized. The response indicates
coverage status, expiration date, and the appropriate service hotline.
Args:
    serial_number (str): Manufacturer serial printed on the appliance label.
Returns:
    str: Warranty summary or an error when the serial number is unregistered.
"""'''

    warranties = {

        'WMX-449201': {'product': 'Front-Load Washer', 'status': 'Active', 'expires': '2026-02-14', 'support': '1-800-555-0191'},

        'FRG-220198': {'product': 'French Door Refrigerator', 'status': 'Expired', 'expires': '2024-09-30', 'support': '1-800-555-0142'},

        'DWS-772310': {'product': 'Dishwasher', 'status': 'Active', 'expires': '2025-12-01', 'support': '1-800-555-0168'},

        'HVAC-903311': {'product': 'Heat Pump', 'status': 'Active', 'expires': '2028-08-19', 'support': '1-800-555-0110'},

    }

    if not serial_number:

        return "Error: 'serial_number' is required."

    record = warranties.get(serial_number.upper())

    if not record:

        return f"Error: Serial number '{serial_number}' not found."

    return (

        f"Product: {record['product']}\n"

        f"Warranty Status: {record['status']}\n"

        f"Expiration Date: {record['expires']}\n"

        f"Service Hotline: {record['support']}"

    )
@mcp.tool()
@safe_tool
def home_energy_usage_report(meter_id: str, billing_cycle: str) -> str:

    '''"""
Provide kWh consumption and cost estimates for a billing cycle.
The dataset includes smart meter readings aggregated by month. Billing cycle must
follow `YYYY-MM`. The tool returns usage, projected bill, and comparison to the
previous month.
Args:
    meter_id (str): Smart meter identifier tied to the household account.
    billing_cycle (str): Billing period in `YYYY-MM` format.
Returns:
    str: Usage report or a descriptive error when no data exists.
"""'''

    usage_history = {

        'MTR-2211': {

            '2025-09': {'kwh': 612, 'cost': 88.45},

            '2025-10': {'kwh': 578, 'cost': 83.12},

        },

        'MTR-9087': {

            '2025-10': {'kwh': 742, 'cost': 109.28},

            '2025-11': {'kwh': 705, 'cost': 103.54},

        },

        'MTR-3344': {

            '2025-08': {'kwh': 455, 'cost': 67.80},

            '2025-09': {'kwh': 498, 'cost': 72.15},

        },

    }

    if not meter_id:

        return "Error: 'meter_id' is required."

    if not billing_cycle:

        return "Error: 'billing_cycle' is required."

    account = usage_history.get(meter_id.upper())

    if not account:

        return f"Error: Meter '{meter_id}' not found."

    current = account.get(billing_cycle)

    if not current:

        return f"No usage recorded for {billing_cycle}."

    year, month = billing_cycle.split('-')

    prev_month = f"{year}-{int(month) - 1:02d}" if int(month) > 1 else None

    previous = account.get(prev_month) if prev_month else None

    comparison = ''

    if previous:

        delta = current['kwh'] - previous['kwh']

        trend = 'higher' if delta > 0 else 'lower'

        comparison = f"\nChange vs previous month: {abs(delta)} kWh {trend}."

    return (

        f"Usage for {billing_cycle}: {current['kwh']} kWh\n"

        f"Estimated Cost: ${current['cost']:.2f}" + comparison

    )
@mcp.tool()
@safe_tool
def neighborhood_watch_alerts(zone: str, severity: str='all') -> str:

    '''"""
List the most recent neighborhood watch alerts for a patrol zone.
Zones correspond to homeowner association sectors. Severity may be filtered by
`info`, `caution`, or `urgent`. By default, all severities are returned.
Args:
    zone (str): Neighborhood zone identifier (e.g., "NW-5").
    severity (str): Optional severity filter. One of `info`, `caution`, `urgent`, or `all`.
Returns:
    str: Formatted alert messages ordered from newest to oldest.
"""'''

    alerts = {

        'NW-1': [

            {'severity': 'info', 'timestamp': '2025-10-31 20:05', 'message': 'Community meeting moved indoors.'},

            {'severity': 'urgent', 'timestamp': '2025-10-30 23:18', 'message': 'Report of suspicious vehicle near Elm St.'},

        ],

        'NW-3': [

            {'severity': 'caution', 'timestamp': '2025-11-01 06:45', 'message': 'Coyotes spotted near the playground.'},

            {'severity': 'info', 'timestamp': '2025-10-29 19:20', 'message': 'Streetlights on Maple Ave restored.'},

        ],

        'NW-5': [

            {'severity': 'urgent', 'timestamp': '2025-10-28 22:40', 'message': 'Car break-in reported on Pine Ct.'},

        ],

    }

    if not zone:

        return "Error: 'zone' is required."

    normalized_zone = zone.upper()

    if severity not in ['info', 'caution', 'urgent', 'all']:

        return "Error: Invalid severity filter."

    zone_alerts = alerts.get(normalized_zone)

    if not zone_alerts:

        return f"No alerts recorded for zone {normalized_zone}."

    filtered = [a for a in zone_alerts if severity == 'all' or a['severity'] == severity]

    if not filtered:

        return f"No alerts matching severity '{severity}' in zone {normalized_zone}."

    lines = [f"[{entry['timestamp']}] ({entry['severity'].upper()}) {entry['message']}" for entry in filtered]

    return "\n".join(lines)
@mcp.tool()
@safe_tool
def school_lunch_menu_lookup(school_code: str, menu_date: str) -> str:

    '''"""
Fetch the cafeteria lunch menu for a given school and date.
Menus include entree, side, and vegetarian alternatives. Dates must follow the
`YYYY-MM-DD` format. Only schools in the lookup table below are supported.
Args:
    school_code (str): District-issued school identifier (e.g., "LMS").
    menu_date (str): Desired menu date in `YYYY-MM-DD` format.
Returns:
    str: Formatted menu details or an informative error.
"""'''

    menus = {

        'LMS': {

            '2025-11-03': {

                'entree': 'Chicken Teriyaki Bowl',

                'side': 'Steamed Broccoli',

                'vegetarian': 'Tofu Stir Fry'

            },

            '2025-11-04': {

                'entree': 'Beef Tacos',

                'side': 'Spanish Rice',

                'vegetarian': 'Black Bean Tacos'

            },

        },

        'NHE': {

            '2025-11-03': {

                'entree': 'Baked Ziti',

                'side': 'Garlic Bread',

                'vegetarian': 'Veggie Ziti'

            },

            '2025-11-05': {

                'entree': 'BBQ Chicken Sandwich',

                'side': 'Coleslaw',

                'vegetarian': 'BBQ Jackfruit Sandwich'

            },

        },

        'WVE': {

            '2025-11-04': {

                'entree': 'Turkey Chili',

                'side': 'Cornbread',

                'vegetarian': 'Three-Bean Chili'

            }

        },

    }

    if not school_code:

        return "Error: 'school_code' is required."

    if not menu_date:

        return "Error: 'menu_date' is required."

    school = menus.get(school_code.upper())

    if not school:

        return f"Error: School '{school_code}' is not supported."

    menu = school.get(menu_date)

    if not menu:

        return f"No menu posted for {menu_date}."

    return (

        f"Entree: {menu['entree']}\n"

        f"Side: {menu['side']}\n"

        f"Vegetarian Option: {menu['vegetarian']}"

    )
@mcp.tool()
@safe_tool
def public_library_book_lookup(title: str, branches: List[str]) -> str:

    '''"""
Check which local library branches have a specific title available for checkout.
The lookup supports partial, case-insensitive matches on book titles. When multiple
entries match the query, all exact branch availability results are returned. The
`branches` parameter should contain at least one branch code to narrow the search.
Args:
    title (str): Full or partial book title to search for.
    branches (List[str]): Preferred branch codes (e.g., ["CEN", "NBE"]).
Returns:
    str: Formatted availability summary or an error message when no copies are found.
"""'''

    catalog = [

        {

            'title': 'Atomic Habits',

            'author': 'James Clear',

            'availability': {'CEN': 4, 'NBE': 1, 'WES': 0}

        },

        {

            'title': 'Project Hail Mary',

            'author': 'Andy Weir',

            'availability': {'CEN': 0, 'NBE': 2, 'EST': 1}

        },

        {

            'title': 'Deep Work',

            'author': 'Cal Newport',

            'availability': {'CEN': 3, 'EST': 1, 'SOU': 2}

        },

        {

            'title': 'The Midnight Library',

            'author': 'Matt Haig',

            'availability': {'NBE': 0, 'WES': 1, 'SOU': 1}

        },

        {

            'title': 'Kitchen Confidential',

            'author': 'Anthony Bourdain',

            'availability': {'CEN': 1, 'EST': 0, 'SOU': 0}

        },

    ]

    if not title:

        return "Error: 'title' is required."

    if not branches:

        return "Error: At least one branch code must be provided."

    normalized_branches = [branch.strip().upper() for branch in branches if branch]

    if not normalized_branches:

        return "Error: Branch list cannot be empty."

    matches = [book for book in catalog if title.lower() in book['title'].lower()]

    if not matches:

        return f"No books found matching '{title}'."

    lines = []

    for book in matches:

        branch_lines = []

        for branch_code in normalized_branches:

            copies = book['availability'].get(branch_code)

            if copies is None:

                branch_lines.append(f"- {branch_code}: not cataloged")

            elif copies == 0:

                branch_lines.append(f"- {branch_code}: all copies checked out")

            else:

                branch_lines.append(f"- {branch_code}: {copies} copy/copies available")

        lines.append(

            f"Title: {book['title']}\n"

            f"Author: {book['author']}\n"

            + '\n'.join(branch_lines)

        )

    return '\n\n'.join(lines)
@mcp.tool()
@safe_tool
def child_homework_tracker(student_id: str, week_start: str) -> str:

    '''"""
Summarize assigned homework tasks for a student during a specific week.
Assignments include subject, due date, and completion status. Week boundaries
use Monday start dates in `YYYY-MM-DD` format.
Args:
    student_id (str): School-issued student identifier.
    week_start (str): Monday date of the week in `YYYY-MM-DD` format.
Returns:
    str: Formatted assignment list or a message when none are assigned.
"""'''

    assignments = {

        'STU-101': {

            '2025-10-27': [

                {'subject': 'Math', 'due': '2025-10-29', 'status': 'In Progress', 'description': 'Worksheet on fractions'},

                {'subject': 'Science', 'due': '2025-10-31', 'status': 'Not Started', 'description': 'Plant cell diagram'},

            ],

            '2025-11-03': [

                {'subject': 'English', 'due': '2025-11-05', 'status': 'Not Started', 'description': 'Read chapter 4 and summarize'},

            ],

        },

        'STU-204': {

            '2025-11-03': [

                {'subject': 'History', 'due': '2025-11-06', 'status': 'In Progress', 'description': 'Timeline of civil rights events'},

                {'subject': 'Math', 'due': '2025-11-07', 'status': 'Complete', 'description': 'Algebra problem set'},

            ],

        },

    }

    if not student_id:

        return "Error: 'student_id' is required."

    if not week_start:

        return "Error: 'week_start' is required."

    student = assignments.get(student_id.upper())

    if not student:

        return f"Error: Student '{student_id}' not found."

    weekly = student.get(week_start)

    if not weekly:

        return f"No assignments recorded for the week starting {week_start}."

    lines = [f"Assignments for week of {week_start}:"]

    for item in weekly:

        lines.append(

            f"- {item['subject']} (Due {item['due']}): {item['status']} - {item['description']}"

        )

    return "\n".join(lines)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

