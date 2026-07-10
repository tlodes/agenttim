"""
MCPAgentBench Code MCP Server.
Concrete FastMCP server with 12 tools for the code domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
import os
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-code")
@mcp.tool()
@safe_tool
def generate_code(prompt: str, language: str, output_name: str,model: str = "gemini-pro",temperature: float=0.4, max_tokens: int=1500, existing_file_path: str='') -> str:

    '''```python
    """
    Generates source code using an AI model based on a given prompt and saves it to a specified file.

    This function utilizes an AI model to generate code in a specified programming language. The generated code
    is then saved to a file with a name and extension derived from the provided output name and language. The
    function allows customization of the AI model's behavior through temperature and token settings and can
    optionally use an existing file as context or reference.

    Args:
        prompt (str): A non-empty string describing the code to be generated.
        language (str): The programming language for the generated code (e.g., 'python', 'javascript').
        model (str): The name of the AI model to use for code generation. Defaults to "gemini-pro".
        output_name (str): The full path including directory and filename (with extension) where the code
            will be saved.
        temperature (float, optional): A float between 0.0 and 1.0 that controls the randomness of the AI model's
            output. Defaults to 0.4.
        max_tokens (int, optional): The maximum number of tokens to generate. Must be a positive integer.
            Defaults to 1500.
        existing_file_path (str, optional): An optional path to an existing file to use as context or reference.

    Returns:
        str: A confirmation message indicating the successful generation and saving of the code file.
    """
```'''

    if not isinstance(prompt, str) or not prompt.strip():

        raise ValueError("Parameter 'prompt' must be a non-empty string.")

    if not isinstance(language, str) or not language.strip():

        raise ValueError("Parameter 'language' must be a non-empty string.")

    if not isinstance(model, str) or not model.strip():

        raise ValueError("Parameter 'model' must be a non-empty string.")

    if not isinstance(output_name, str) or not output_name.strip():

        raise ValueError("Parameter 'output_name' must be a non-empty string.")

    if not isinstance(temperature, float) or not 0.0 <= temperature <= 1.0:

        raise ValueError("Parameter 'temperature' must be a float between 0.0 and 1.0.")

    if not isinstance(max_tokens, int) or max_tokens <= 0:

        raise ValueError("Parameter 'max_tokens' must be a positive integer.")

    if not isinstance(existing_file_path, str):

        raise ValueError("Parameter 'existing_file_path' must be a string.")

    import re

    import datetime

    clean_prompt = re.sub('[^\\w\\s-]', '', prompt.lower())

    clean_prompt = re.sub('[-\\s]+', '_', clean_prompt)

    clean_prompt = clean_prompt[:20]

    filename = output_name

    return f'Code has been generated successfully and saved to {filename}'
@mcp.tool()
@safe_tool
def analyze_code(path: str, language: str) -> str:

    '''```python
    """
    Analyzes the specified code file for bugs, errors, and functionality issues, and
    returns the path where the analysis report would be saved.

    Args:
        path (str): The file path of the code to be analyzed. Must be a non-empty string.
        language (str): The programming language of the code. Accepted values are
            'javascript', 'typescript', 'html', 'css', 'python', 'auto', 'cpp', 'cuda'.
            Use 'auto' to automatically detect the language based on the file extension.

    Returns:
        str: A message indicating the completion of the analysis, including the path where
        the analysis report would be saved. If no issues are found, the message will indicate that
        no known issues were detected.
    """
```'''

    mock_analysis_db = {'C:/Users/user/Desktop/MyProject/src/device_struct.cu': {'language': 'cuda', 'issues': [{'type': 'memory', 'description': 'Pointer members in struct are only shallow copied to device memory. This causes invalid memory access when dereferenced on GPU.', 'line': 42, 'suggestion': "Allocate memory for pointer members on device separately, then copy the data, and update the struct's device pointer."}, {'type': 'complexity', 'description': 'Memory allocation and copy logic is duplicated for multiple structs with nested pointers.', 'line': None, 'suggestion': 'Refactor allocation and copy logic into utility functions to reduce duplication and potential bugs.'}]}, 'python_project/script.py': {'language': 'python', 'issues': [{'type': 'syntax', 'description': 'Missing colon at end of function definition.', 'line': 10, 'suggestion': "Add ':' at the end of the function definition."}]}}

    if not isinstance(path, str) or not path.strip():

        raise ValueError("Invalid 'path': must be a non-empty string.")

    if not isinstance(language, str) or language.lower() not in ['javascript', 'typescript', 'html', 'css', 'python', 'auto', 'cpp', 'cuda']:

        raise ValueError("Invalid 'language': must be one of ['javascript', 'typescript', 'html', 'css', 'python', 'auto', 'cpp', 'cuda'].")

    path_key = path.strip()

    lang_key = language.lower()

    if lang_key == 'auto':

        if path_key.endswith('.cu'):

            lang_key = 'cpp'

        elif path_key.endswith('.py'):

            lang_key = 'python'

        else:

            lang_key = 'unknown'

    analysis_result = mock_analysis_db.get(path_key)

    if not analysis_result:

        directory = os.path.dirname(path_key)

        base_name = os.path.basename(path_key)

        name_parts = os.path.splitext(base_name)

        analysis_filename = f'{name_parts[0]}_analysis_report.txt'

        analysis_file_path = os.path.join(directory, analysis_filename)

        analyzed_file_abs_path = os.path.abspath(path_key)

        analysis_file_abs_path = os.path.abspath(analysis_file_path)

        return f"Analysis complete for '{path_key}' ({lang_key}). No known issues found. Analysis report would be saved to: {analysis_file_abs_path}"

    issues_found = analysis_result['issues']

    directory = os.path.dirname(path_key)

    base_name = os.path.basename(path_key)

    name_parts = os.path.splitext(base_name)

    analysis_filename = f'{name_parts[0]}_analysis_report.txt'

    analysis_file_path = os.path.join(directory, analysis_filename)

    analyzed_file_abs_path = os.path.abspath(path_key)

    analysis_file_abs_path = os.path.abspath(analysis_file_path)

    report_content = []

    report_content.append(f'=== Code Analysis Report ===\n')

    report_content.append(f'Analyzed file: {analyzed_file_abs_path}')

    report_content.append(f'Language: {lang_key}')

    report_content.append(f"Analysis date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    save_issues = bool(issues_found)

    if save_issues:

        report_content.append(f'=== ISSUES FOUND ({len(issues_found)} issues) ===\n')

        for (idx, issue) in enumerate(issues_found, 1):

            line_info = f" at line {issue['line']}" if issue['line'] else ''

            report_content.append(f"Issue #{idx} - [{issue['type'].capitalize()} Issue]{line_info}")

            report_content.append(f"Description: {issue['description']}")

            report_content.append(f"Code Modification Suggestion: {issue['suggestion']}")

            report_content.append('')

    else:

        report_content.append('No issues identified.\n')

    report_content.append(f'=== SUMMARY ===')

    report_content.append(f'Total issues found: {len(issues_found)}')

    if save_issues:

        report_content.append(f'Review the detailed modification suggestions above to improve code quality and functionality.')

    saved_content = '\n'.join(report_content)

    return f'Analysis complete. File analyzed: {analyzed_file_abs_path}. Issues and code modification suggestions would be saved to: {analysis_file_abs_path}'
@mcp.tool()
@safe_tool
def execute_python_code(code_dir: str) -> str:

    '''```python
    """
    Executes a Python file at the specified path.

    This function takes a file path as input and executes the Python file
    located at that path. It ensures that the file path provided is
    a non-empty string pointing to a valid Python file.

    Args:
        code_dir (str): The path to the Python file to be executed.
                        Must be a non-empty string pointing to a .py file.
                        Example: "./a.py", "/path/to/script.py", "C:/scripts/example.py"

    Returns:
        str: A message indicating the successful execution of the Python file.

    Raises:
        ValueError: If 'code_dir' is not a non-empty string.

    Example:
        execute_python_code("./a.py")
        # Returns: "Python code successfully executed in directory: ./a.py"
    """
```'''

    if not isinstance(code_dir, str) or not code_dir.strip():

        raise ValueError("Parameter 'code_dir' must be a non-empty string.")

    if not code_dir.strip():

        return f"Error: Invalid file path '{code_dir}'."

    result = f'Python code successfully executed in directory: {code_dir}'

    return result
@mcp.tool()
@safe_tool
def Semgrep_Code_SAST(path: str, ruleset: str, config_file: str, output_format: str) -> str:

    '''```python
    """
    A static application security testing tool that minimizes noise and empowers
    developers to fix issues with tailored remediation guidance.

    This function performs a security scan on the specified codebase using Semgrep
    rulesets, providing detailed reports on identified security issues along with
    remediation suggestions.

    Args:
        path (str): The file path to the codebase to be scanned. Must be a string.
        ruleset (str): The Semgrep ruleset to apply during the scan. Must be a non-empty string.
        config_file (str): The configuration file for Semgrep settings. Must be a non-empty string.
        output_format (str): The format for the output report. Supported formats are 'json' and 'text'.

    Returns:
        str: A formatted string containing the security scan report, either in JSON or text format,
             based on the specified output_format. The report includes a summary of issues found and
             detailed remediation guidance for each issue.
    """
```'''

    mock_scan_results = {'security': {'json': {'summary': {'total_issues': 3, 'critical': 1, 'high': 1, 'medium': 1, 'low': 0}, 'issues': [{'id': 'SQLI-001', 'type': 'SQL Injection', 'file': 'app/controllers/user_controller.py', 'line': 87, 'severity': 'critical', 'description': 'Unescaped user input in SQL query construction.', 'remediation': 'Use parameterized queries with placeholders.'}, {'id': 'XSS-002', 'type': 'Cross-Site Scripting', 'file': 'app/templates/profile.html', 'line': 42, 'severity': 'high', 'description': 'Unsanitized user input rendered in HTML.', 'remediation': 'Sanitize inputs before rendering.'}, {'id': 'GEN-003', 'type': 'Hardcoded Secret', 'file': 'app/config.py', 'line': 10, 'severity': 'medium', 'description': 'Hardcoded API key found.', 'remediation': 'Remove hardcoded secrets and use environment variables.'}]}, 'text': '=== Semgrep Security Scan Report ===\nCritical: SQL Injection in app/controllers/user_controller.py:87\n    Remediation: Use parameterized queries with placeholders.\nHigh: XSS in app/templates/profile.html:42\n    Remediation: Sanitize inputs before rendering.\nMedium: Hardcoded Secret in app/config.py:10\n    Remediation: Use environment variables instead of hardcoded secrets.\nTotal issues: 3'}, 'sql-injection': {'json': {'summary': {'total_issues': 1, 'critical': 1, 'high': 0, 'medium': 0, 'low': 0}, 'issues': [{'id': 'SQLI-001', 'type': 'SQL Injection', 'file': 'db/query_handler.py', 'line': 56, 'severity': 'critical', 'description': 'Direct string concatenation with user input in SQL statement.', 'remediation': 'Switch to parameterized queries.'}]}, 'text': '=== Semgrep SQL Injection Scan ===\nCritical: SQL Injection in db/query_handler.py:56\n    Remediation: Switch to parameterized queries.\nTotal issues: 1'}, 'xss': {'json': {'summary': {'total_issues': 1, 'critical': 0, 'high': 1, 'medium': 0, 'low': 0}, 'issues': [{'id': 'XSS-002', 'type': 'Cross-Site Scripting', 'file': 'templates/comment.html', 'line': 23, 'severity': 'high', 'description': 'Unsanitized user-supplied data inserted into page.', 'remediation': 'Escape HTML output or use a templating engine with auto-escaping.'}]}, 'text': '=== Semgrep XSS Scan ===\nHigh: XSS in templates/comment.html:23\n    Remediation: Escape HTML output or use auto-escaping.\nTotal issues: 1'}}

    if not ruleset or not isinstance(ruleset, str):

        raise ValueError("Invalid or missing 'ruleset' parameter. Must be a non-empty string.")

    if not config_file or not isinstance(config_file, str):

        raise ValueError("Invalid or missing 'config_file' parameter. Must be a non-empty string.")

    if not output_format or not isinstance(output_format, str):

        raise ValueError("Invalid or missing 'output_format' parameter. Must be a non-empty string.")

    if path is not None and (not isinstance(path, str)):

        raise ValueError("'path' parameter must be a string if provided.")

    ruleset_key = ruleset.lower()

    fmt_key = output_format.lower()

    if ruleset_key not in mock_scan_results:

        if fmt_key == 'json':

            return str({'summary': {'total_issues': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}, 'issues': []})

        elif fmt_key == 'text':

            return '=== Semgrep Scan Report ===\nNo issues found.'

        else:

            raise ValueError("Unsupported output_format. Supported: 'json', 'text'.")

    if fmt_key not in mock_scan_results[ruleset_key]:

        raise ValueError("Unsupported output_format. Supported: 'json', 'text'.")

    return str(mock_scan_results[ruleset_key][fmt_key])
@mcp.tool()
@safe_tool
def patch_file(path: str, changes_path: str) -> str:

    '''```python
    """
    Applies modifications to a specified file based on patch instructions from another file.

    This function reads a series of search and replace operations from a file specified by
    `changes_path` and applies these modifications to the target file located at `path`.

    Args:
        path (str): The file path of the target file to which changes will be applied.
                    Must be a non-empty string.
        changes_path (str): The file path containing the patch instructions.
                            Must be a non-empty string.

    Returns:
        str: A confirmation message indicating that the modifications have been completed
             and saved to the specified target file.
    """
```'''

    if not isinstance(path, str) or not path.strip():

        raise ValueError("Invalid 'path' parameter. Must be a non-empty string.")

    if not isinstance(changes_path, str) or not changes_path.strip():

        raise ValueError("Invalid 'changes_path' parameter. Must be a non-empty string.")

    return f'Modifications completed and saved in file: {path}'
@mcp.tool()
@safe_tool
def search_and_read_files(path: str) -> str:

    '''```python
    """
    Scans the specified directory path for files and returns a message
    indicating the topic of the files found.

    Args:
        path (str): A non-empty string representing the directory path to scan
                    for files. The path should be in a valid format such as
                    "/path/to/directory", "./relative/path", or "C:/Windows/path".

    Returns:
        str: A message indicating the topic of the files located in the specified
             directory.

    Raises:
        ValueError: If the 'path' parameter is not a valid non-empty string.
    """
```'''

    mock_file_database = {'/research/document': ['myResearch.docx', 'paper1.pdf', 'paper2.pdf', 'notes.txt', 'research_summary.pdf']}

    if not isinstance(path, str) or not path.strip():

        raise ValueError("Parameter 'path' must be a non-empty string representing a valid directory path.")

    normalized_path = path.strip()

    if normalized_path in mock_file_database:

        file_count = len(mock_file_database[normalized_path])

        return 'The topic of these files is about MOE, subject is large language model'

    else:

        return 'The topic of these files is about MOE, subject is large language model'
@mcp.tool()
@safe_tool
def convert_pdf_to_markdown(pdf_dir: str) -> str:

    '''```python
"""
Converts PDF files located in the specified directory to Markdown format.
This function processes all PDF files found within the given directory path,
converting each one to a corresponding Markdown file. The directory path must
be a valid, non-empty string.
Args:
    pdf_dir (str): The directory path containing the PDF file(s) to be converted.
                   It should be a valid path pointing to the location of the PDF files.
Returns:
    str: A message indicating that all PDF files have been successfully converted
         to Markdown format.
"""
```'''

    if not isinstance(pdf_dir, str) or not pdf_dir.strip():

        raise ValueError('Invalid pdf_dir: must be a non-empty string.')

    return 'All PDF files have been converted to Markdown format.'
@mcp.tool()
@safe_tool
def create_ui(description: str) -> str:

    '''```python
    """
    Generates web UI components using shadcn/ui components and Tailwind CSS.

    This function creates a web user interface based on the provided description.
    It utilizes shadcn/ui components and Tailwind CSS to build responsive and
    visually appealing UI elements. Use this function when the description
    includes references to UI requirements.

    Args:
        description (str): A non-empty string describing the type of UI to create.
            It should contain keywords like 'e-commerce' or 'flight' to select
            specific UI templates.

    Returns:
        str: A message indicating the successful creation of UI components
        tailored to the specified description using shadcn/ui and Tailwind CSS.
    """
```'''

    mock_ui_templates = {'ecommerce_frontend': {'description': 'A responsive e-commerce front-end using shadcn/ui components and Tailwind CSS.', 'components': ['ProductCard with image, name, price, and Add to Cart button', 'ProductGrid to display multiple ProductCards', 'SearchBar with real-time filtering', 'ShoppingCartSidebar with item list and checkout button'], 'notes': 'Data binding to product API endpoints, responsive for desktop and mobile.'}, 'flight_display': {'description': 'A flight information display board component using shadcn/ui and Tailwind CSS.', 'components': ['Table with columns: Flight No, Destination, Departure Time, Status', 'StatusBadge component with color coding', 'RefreshButton to reload flight data'], 'notes': 'Real-time updates via WebSocket or polling.'}}

    if not isinstance(description, str) or not description.strip():

        raise ValueError("Invalid input: 'description' must be a non-empty string.")

    desc_lower = description.lower()

    selected_template = None

    if 'e-commerce' in desc_lower or 'ecommerce' in desc_lower:

        selected_template = mock_ui_templates['ecommerce_frontend']

    elif 'flight' in desc_lower:

        selected_template = mock_ui_templates['flight_display']

    if selected_template:

        return f"UI components for '{selected_template['description']}' created successfully using shadcn/ui and Tailwind CSS."

    else:

        return 'UI components created successfully using shadcn/ui and Tailwind CSS.'
@mcp.tool()
@safe_tool
def figma_export_code(fileKey: str, nodeId: str) -> str:

    '''```python
    """
    Converts Figma design files into production-ready code snippets.

    This function facilitates the design-to-development workflow by allowing
    developers to fetch entire Figma files or specific nodes and export them
    as code. It is particularly useful for building UI components, prototyping
    applications, and accelerating product development.

    Args:
        fileKey (str): The unique identifier for the Figma file to be exported.
                       Must be a non-empty string.
        nodeId (str): The unique identifier for a specific node within the Figma
                      file. If provided, must be a non-empty string.

    Returns:
        str: A message indicating the success of the export operation, along with
             the corresponding code snippet. If a nodeId is specified, the code
             for that node and its parameters are returned. Otherwise, the full
             file code and parameters for all nodes are returned.
    """
```'''

    mock_figma_db = {'UI123VOCABAPP': {'full_file_code': "<App>\n  <Header title='Vocab Memorizer'/>\n  <WordCard word='example' />\n  <CountdownTimer duration='60' />\n</App>", 'nodes': {'NODE_HEADER': {'code': "<Header title='Vocab Memorizer' style={{ backgroundColor: '#4CAF50', color: 'white' }}/>", 'params': {'title': 'Vocab Memorizer', 'backgroundColor': '#4CAF50', 'color': 'white'}}, 'NODE_CARD': {'code': "<WordCard word='example' definition='A representative form or pattern'/>", 'params': {'word': 'example', 'definition': 'A representative form or pattern', 'cardId': 'card_001'}}, 'NODE_TIMER': {'code': "<CountdownTimer start={Date.now()} duration={60000} onComplete={alert('Time up!')}/>", 'params': {'Ele': 'vocab_timer_user001', 'StartDate': '2025-07-15T09:00:00', 'EndDate': '20245-08-15T09:30:00'}}}}}

    if not isinstance(fileKey, str) or not fileKey.strip():

        raise ValueError('Invalid fileKey: must be a non-empty string.')

    if fileKey not in mock_figma_db:

        raise ValueError(f"Figma file with key '{fileKey}' not found in the mock database.")

    if nodeId:

        if not isinstance(nodeId, str) or not nodeId.strip():

            raise ValueError('Invalid nodeId: must be a non-empty string when provided.')

        if nodeId not in mock_figma_db[fileKey]['nodes']:

            raise ValueError(f"Node '{nodeId}' not found in file '{fileKey}'.")

        node_data = mock_figma_db[fileKey]['nodes'][nodeId]

        if isinstance(node_data, dict) and 'code' in node_data:

            result = f"Export successful: Code for node '{nodeId}'\n{node_data['code']}"

            if 'params' in node_data and node_data['params']:

                params = node_data['params']

                result += f'\n\nParameters for {nodeId}:\n'

                for (param_name, param_value) in params.items():

                    result += f'{param_name}: {param_value}\n'

            return result

        else:

            return f"Export successful: Code for node '{nodeId}'\n{node_data}"

    file_data = mock_figma_db[fileKey]

    result = f"Export successful: Full file code for '{fileKey}'\n{file_data['full_file_code']}"

    if 'nodes' in file_data:

        result += f'\n\nNode Parameters:\n'

        for (node_name, node_data) in file_data['nodes'].items():

            if isinstance(node_data, dict) and 'params' in node_data and node_data['params']:

                result += f'\n{node_name}:\n'

                for (param_name, param_value) in node_data['params'].items():

                    result += f'  {param_name}: {param_value}\n'

    return result
@mcp.tool()
@safe_tool
def add_site(domains: list) -> str:

    '''```python
    """
    Create a new PHP website for the specified domain names.

    This function registers a new PHP website using the provided list of domain
    names. It checks for the validity of the domains and ensures that they do
    not already exist. If any domain contains the word "music", the website is
    initialized as an online music review platform with sample content.

    Args:
        domains (list of str): A list of domain names for the new website. Each
            domain must be a non-empty string.

    Returns:
        str: A message indicating the success of the website creation or an
        error message if the input is invalid or if any domain already exists.
    """
```'''

    if not hasattr(add_site, 'mock_db'):

        add_site.mock_db = {'sites': []}

    if not isinstance(domains, list):

        return "Error: 'domains' must be a list of domain names."

    if not domains:

        return 'Error: You must provide at least one domain for the new website.'

    for d in domains:

        if not isinstance(d, str) or not d.strip():

            return f"Error: Invalid domain '{d}'. Domains must be non-empty strings."

    existing_domains = {domain for site in add_site.mock_db['sites'] for domain in site['domains']}

    duplicates = [d for d in domains if d in existing_domains]

    if duplicates:

        return f"Error: The following domain(s) already exist: {', '.join(duplicates)}"

    new_site_id = len(add_site.mock_db['sites']) + 1

    site_entry = {'id': new_site_id, 'domains': domains, 'type': 'PHP', 'description': 'A newly created PHP website.', 'created_at': '2024-06-01 10:00:00', 'posts': [], 'comments': []}

    if any(('music' in d.lower() for d in domains)):

        site_entry['description'] = 'An online music review platform in PHP that features music reviews and recommendations.'

        site_entry['posts'].append({'post_id': 1, 'title': 'Top 10 Albums of the Year', 'content': 'Our music experts review the top 10 albums of this year with in-depth analysis and recommendations.', 'comments': [{'comment_id': 1, 'content': 'Great list! I agree with most of the picks.'}, {'comment_id': 2, 'content': 'I think you missed a few underground gems.'}]})

    add_site.mock_db['sites'].append(site_entry)

    return f"PHP website created successfully for domains: {', '.join(domains)}"
@mcp.tool()
@safe_tool
def stagehand_act(action: str, variables: dict) -> str:

    '''```python
    """
    Performs a specific atomic action on a web page element.

    This function executes actions such as clicking a button or typing text into
    an input field. It is designed to handle single-step actions only, ensuring
    that each action is as specific and granular as possible. Examples of valid
    actions include 'Click the sign in button' or 'Type 'hello' into the search
    input'. Multi-step actions like 'Order me pizza' or 'Send an email to Paul
    asking him to call me' should be avoided.

    Args:
        action (str): The action to perform on the web page element. This should
            be a single-step command, such as 'click' or 'type'.
        variables (dict): A dictionary containing additional parameters required
            for the action. Must include 'element' to specify the target element
            and may include 'text' for typing actions or 'selection' for list
            selection actions.

    Returns:
        str: A message indicating the result of the action performed, such as
        confirmation of a successful click or type action, or an error message
        if the action could not be completed.
    """
```'''

    mock_page_elements = {'search_button': {'type': 'button', 'label': 'Search', 'state': 'enabled'}, 'location_permission_popup': {'type': 'popup', 'label': 'Allow location access', 'state': 'visible'}, 'search_input': {'type': 'input', 'label': 'Enter restaurant name or cuisine', 'value': ''}, 'filter_button': {'type': 'button', 'label': 'Filters', 'state': 'enabled'}, 'restaurant_list': {'type': 'list', 'items': []}}

    if not isinstance(action, str):

        raise ValueError("Parameter 'action' must be a string.")

    if not isinstance(variables, dict):

        raise ValueError("Parameter 'variables' must be an object (dict).")

    target_element = variables.get('element')

    if not target_element or target_element not in mock_page_elements:

        raise ValueError(f"Target element '{target_element}' not found in mock page elements.")

    element = mock_page_elements[target_element]

    action_lower = action.lower()

    if 'click' in action_lower:

        if element['type'] == 'button' and element['state'] == 'enabled':

            return f"Clicked the '{element['label']}' button successfully."

        elif element['type'] == 'popup' and element['state'] == 'visible':

            return f"Clicked '{element['label']}' and dismissed the popup."

        else:

            return f"Cannot click on '{element['label']}' because it is not clickable or not enabled."

    elif 'type' in action_lower or 'enter' in action_lower:

        text_to_type = variables.get('text')

        if element['type'] == 'input':

            if not isinstance(text_to_type, str) or not text_to_type.strip():

                raise ValueError("You must provide a non-empty 'text' string to type into the input.")

            element['value'] = text_to_type

            return f"Typed '{text_to_type}' into the '{element['label']}' input field."

        else:

            return f"Cannot type into '{element['label']}' because it is not an input field."

    elif 'select' in action_lower:

        if element['type'] == 'list' and element['items']:

            selection = variables.get('selection')

            if selection in element['items']:

                return f"Selected '{selection}' from the restaurant list."

            else:

                return f"'{selection}' is not available in the restaurant list."

        else:

            return f"No items available to select in '{element['label']}'."

    else:

        return f"Action '{action}' is not supported for element '{element['label']}'."
@mcp.tool()
@safe_tool
def stagehand_navigate(url: str) -> str:

    '''```python
"""
Navigates to a specified URL in the browser.
This function attempts to open the given URL in a web browser. It is recommended to use URLs that are reliable and expected to remain accessible. If the specified URL is not recognized, the function defaults to using 'https://google.com' as the starting point.
Args:
    url (str): The URL to navigate to. Must be a non-empty string.
Returns:
    str: A message indicating the result of the navigation attempt.
"""
```'''

    mock_url_db = {'https://maps.google.com/search/restaurants': 'Navigated to Google Maps search for nearby restaurants.', 'https://yelp.com/search?find_desc=restaurants&find_loc=current+location': 'Opened Yelp restaurant search results based on current location.', 'https://tripadvisor.com/Restaurants': "Opened TripAdvisor's restaurant listings page.", 'https://google.com': 'Opened Google homepage.'}

    if not isinstance(url, str):

        raise ValueError("Parameter 'url' must be a string.")

    if not url.strip():

        raise ValueError("Parameter 'url' cannot be empty.")

    if url in mock_url_db:

        return mock_url_db[url]

    else:

        return mock_url_db['https://google.com']
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

