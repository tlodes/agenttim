"""
MCPAgentBench Calendar MCP Server.
Concrete FastMCP server with 5 tools for the calendar domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-calendar")
@mcp.tool()
@safe_tool
def create_event(subject: str, startDate: str = None, startTime: str = None, endDate: str = None, endTime: str = None, location: str = None, isMeeting: bool = False, attendees: str = None) -> str:

    '''"""
Create a new calendar event or meeting with specified details.
This function allows you to create an event by providing information such as
subject, start and end times, location, description, and attendees. It supports
both all-day events and timed meetings, and can add the event to a specified calendar.
Args:
    subject (str, required): The title or subject of the event.
    startDate (str, required): Start date in 'MM/DD' format.
    startTime (str, optional): Start time in 'HH:MM' format, where the hour is in 24-hour format.
    endDate (str, required): End date in 'MM/DD' format.
    endTime (str, optional): End time in 'HH:MM' format, where the hour is in 24-hour format.
    location (str, required): The location where the event will take place.
    isMeeting (bool, optional): Whether the event is a meeting. Defaults to False.
    attendees (str, optional): A semicolon-separated list of attendee email addresses. Required if isMeeting is True.
Returns:
    str: A confirmation message if the event is created successfully, or an error message if validation fails.
"""'''

    import datetime

    mock_calendar_db = {'default': [], 'personal': [], 'work': []}

    try:

        start_datetime = datetime.datetime.strptime(f'{startDate} {startTime}', '%m/%d %H:%M') if startDate and startTime else None

    except ValueError:

        return 'Error: Invalid start date or time format. Please use MM/DD for dates and HH:MM for times.'

    if endDate and endTime:

        try:

            end_datetime = datetime.datetime.strptime(f'{endDate} {endTime}', '%m/%d %H:%M')

            if end_datetime <= start_datetime:

                return 'Error: End date and time must be after start date and time.'

        except ValueError:

            return 'Error: Invalid end date or time format. Please use MM/DD for dates and HH:MM for times.'

    else:

        end_datetime = None

    event = {'subject': subject, 'start': start_datetime, 'end': end_datetime, 'location': location, 'isMeeting': isMeeting, 'attendees': attendees.split(';') if attendees else []}

    mock_calendar_db['default'].append(event)

    confirmation_message = f"Event '{subject}' has been created on the default calendar.\n"

    if start_datetime:

        confirmation_message += f"Start: {start_datetime.strftime('%m/%d %H:%M')}\n"

    if end_datetime:

        confirmation_message += f"End: {end_datetime.strftime('%m/%d %H:%M')}\n"

    if location:

        confirmation_message += f'Location: {location}\n'

    if isMeeting and attendees:

        confirmation_message += f"Attendees: {', '.join(event['attendees'])}\n"

    return confirmation_message
@mcp.tool()
@safe_tool
def list_events(date: str) -> str:

    '''"""
List events scheduled for a specific date.
The date must be provided in the format ``MM/DD`` (e.g., ``05/06``).
If events are found for the specified date, their details, including title, status, and attendees, will be returned.
If no events match the date, an appropriate message will be returned.
Args:
    date (str): The date to search for events, in ``MM/DD`` format.
Returns:
    str: A formatted string listing the events for the given date, including their status and attendees,
         or a message indicating that no events were found or that the date format is invalid.
"""'''

    from datetime import datetime

    mock_events = [{'date': '05/06', 'title': 'Meeting with Bob', 'attendees': ['Alice', 'Bob'], 'status': 'confirmed'}, {'date': '05/06', 'title': 'Lunch with Sarah', 'attendees': ['Alice', 'Sarah'], 'status': 'tentative'}, {'date': '03/13', 'title': 'Project Presentation', 'attendees': ['Alice', 'Charlie'], 'status': 'confirmed'}, {'date': '04/01', 'title': "April Fool's Day Event", 'attendees': ['Alice'], 'status': 'confirmed'}, {'date': '04/06', 'title': 'Yoga Class', 'attendees': ['Alice'], 'status': 'confirmed'}]

    try:

        date_obj = datetime.strptime(date, '%m/%d')

    except ValueError:

        return 'Invalid date format. Please use MM/DD.'

    filtered_events = []

    for event in mock_events:

        event_date_obj = datetime.strptime(event['date'], '%m/%d')

        if event_date_obj == date_obj:

            filtered_events.append(event)

    if not filtered_events:

        return 'No events found for the specified date.'

    output = 'Events:\n'

    for event in filtered_events:

        output += f"- {event['date']}: {event['title']} (Status: {event['status']})\n"

        output += f"  Attendees: {', '.join(event['attendees'])}\n"

    return output
@mcp.tool()
@safe_tool
def find_free_slots(date: str) -> str:

    '''"""
Find free time slots within a given date range.
The date should be provided in the format ``MM/DD``. Do not infer or assume any date that is not explicitly provided.
Args:
    date (str): The date for which to find available time slots, in ``MM/DD`` format.
Returns:
    str: A message indicating the available free time slots for the specified date.
"""'''

    return 'The user is free from 7:00 PM to 10:00 PM on ' + date + '.'
@mcp.tool()
@safe_tool
def create_task(title: str, description: str, due_date: str, priority: int) -> str:

    '''```python
"""
Creates a new task in TickTick with specified details.
This function allows you to create a task by providing essential information such as the title, description, due date, and priority level. It validates the input parameters to ensure they meet the required formats and constraints.
Args:
    title (str): The title of the task. Must be a non-empty string.
    description (str): The content or description of the task. Optional; if provided, must be a string.
    due_date (str): The due date for the task. Optional; if provided, must be a string. should be in 'YYYY-MM-DD' format.
    priority (int): The priority level of the task, ranging from 0 (lowest) to 3 (highest). Must be an integer within this range.
Returns:
    str: A confirmation message indicating the successful creation of the task, or an error message if validation fails.
"""
```'''

    if not isinstance(title, str) or not title.strip():

        return "Error: 'title' must be a non-empty string."

    if description is not None and (not isinstance(description, str)):

        return "Error: 'description' must be a string if provided."

    if due_date is not None and (not isinstance(due_date, str)):

        return "Error: 'due_date' must be a string if provided."

    if priority is not None:

        if not isinstance(priority, int) or priority < 0 or priority > 3:

            return "Error: 'priority' must be an integer between 0 and 3."

    return f"Task '{title}' has been created successfully."
@mcp.tool()
@safe_tool
def update_task(task_id: str, task_name: str, content: str, due_date: str, priority: int) -> str:

    '''```python
"""
Updates an existing task in TickTick with new details.
This function allows you to modify an existing task's name, content, due date, and priority level in the TickTick task management system.
Args:
    task_id (str): The unique identifier of the task to be updated. Must be a non-empty string.
    task_name (str): The new name for the task. If provided, must be a string.
    content (str): The new content or description for the task. If provided, must be a string.
    due_date (str): The new due date for the task. If provided, must be a string. should be in 'YYYY-MM-DD' format.
    priority (int): The new priority level for the task, ranging from 0 (lowest) to 3 (highest). Must be an integer within this range.
Returns:
    str: A confirmation message indicating that the task has been successfully updated.
"""
```'''

    if not isinstance(task_id, str) or not task_id.strip():

        return "Error: 'task_id' must be a non-empty string."

    if task_name is not None and (not isinstance(task_name, str)):

        return "Error: 'task_name' must be a string if provided."

    if content is not None and (not isinstance(content, str)):

        return "Error: 'content' must be a string if provided."

    if due_date is not None and (not isinstance(due_date, str)):

        return "Error: 'due_date' must be a string if provided."

    if priority is not None:

        if not isinstance(priority, int) or priority < 0 or priority > 3:

            return "Error: 'priority' must be an integer between 0 and 3."

    return f"Task '{task_id}' has been updated successfully."
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

