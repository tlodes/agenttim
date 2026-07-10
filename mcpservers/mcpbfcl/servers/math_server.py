"""
BFCL Math MCP Server.
Wraps MathAPI as MCP tools for the BFCL benchmark.
"""
import json
from typing import List
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.math_api import MathAPI
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-math")
_instance = MathAPI()
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """Load a scenario configuration into the MathAPI instance.

    MathAPI is stateless so this is a no-op, but kept for interface consistency.

    Args:
        config_json (str): JSON string with the scenario configuration.
        long_context (bool): If True, extend state with long-context data.

    Returns:
        str: "OK" on success.
    """

    return "OK"
@mcp.tool()
def admin_get_state() -> str:

    """Return the current public state of the MathAPI as JSON.

    Returns:
        str: JSON string of all public attributes.
    """

    state = {

        attr: val

        for attr, val in vars(_instance).items()

        if not attr.startswith("_")

    }

    return json.dumps(state, default=str)
@mcp.tool()
@safe_tool
def logarithm(value: float, base: float, precision: int) -> str:

    """Compute the logarithm of a number with adjustable precision using mpmath.

    Args:
        value (float): The number to compute the logarithm of.
        base (float): The base of the logarithm.
        precision (int): Desired precision for the result.

    Returns:
        result (float): The logarithm of the number with respect to the given base.
    """

    return json.dumps(

        _instance.logarithm(value=value, base=base, precision=precision),

        default=str,

    )
@mcp.tool()
@safe_tool
def mean(numbers: List[float]) -> str:

    """Calculate the mean of a list of numbers.

    Args:
        numbers (List[float]): List of numbers to calculate the mean of.

    Returns:
        result (float): Mean of the numbers.
    """

    return json.dumps(_instance.mean(numbers=numbers), default=str)
@mcp.tool()
@safe_tool
def standard_deviation(numbers: List[float]) -> str:

    """Calculate the standard deviation of a list of numbers.

    Args:
        numbers (List[float]): List of numbers to calculate the standard deviation of.

    Returns:
        result (float): Standard deviation of the numbers.
    """

    return json.dumps(_instance.standard_deviation(numbers=numbers), default=str)
@mcp.tool()
@safe_tool
def si_unit_conversion(value: float, unit_in: str, unit_out: str) -> str:

    """Convert a value from one SI unit to another.

    Args:
        value (float): Value to be converted.
        unit_in (str): Unit of the input value.
        unit_out (str): Unit to convert the value to.

    Returns:
        result (float): Converted value in the new unit.
    """

    return json.dumps(

        _instance.si_unit_conversion(value=value, unit_in=unit_in, unit_out=unit_out),

        default=str,

    )
@mcp.tool()
@safe_tool
def imperial_si_conversion(value: float, unit_in: str, unit_out: str) -> str:

    """Convert a value between imperial and SI units.

    Args:
        value (float): Value to be converted.
        unit_in (str): Unit of the input value.
        unit_out (str): Unit to convert the value to.

    Returns:
        result (float): Converted value in the new unit.
    """

    return json.dumps(

        _instance.imperial_si_conversion(

            value=value, unit_in=unit_in, unit_out=unit_out

        ),

        default=str,

    )
@mcp.tool()
@safe_tool
def add(a: float, b: float) -> str:

    """Add two numbers.

    Args:
        a (float): First number.
        b (float): Second number.

    Returns:
        result (float): Sum of the two numbers.
    """

    return json.dumps(_instance.add(a=a, b=b), default=str)
@mcp.tool()
@safe_tool
def subtract(a: float, b: float) -> str:

    """Subtract one number from another.

    Args:
        a (float): Number to subtract from.
        b (float): Number to subtract.

    Returns:
        result (float): Difference between the two numbers.
    """

    return json.dumps(_instance.subtract(a=a, b=b), default=str)
@mcp.tool()
@safe_tool
def multiply(a: float, b: float) -> str:

    """Multiply two numbers.

    Args:
        a (float): First number.
        b (float): Second number.

    Returns:
        result (float): Product of the two numbers.
    """

    return json.dumps(_instance.multiply(a=a, b=b), default=str)
@mcp.tool()
@safe_tool
def divide(a: float, b: float) -> str:

    """Divide one number by another.

    Args:
        a (float): Numerator.
        b (float): Denominator.

    Returns:
        result (float): Quotient of the division.
    """

    return json.dumps(_instance.divide(a=a, b=b), default=str)
@mcp.tool()
@safe_tool
def power(base: float, exponent: float) -> str:

    """Raise a number to a power.

    Args:
        base (float): The base number.
        exponent (float): The exponent.

    Returns:
        result (float): The base raised to the power of the exponent.
    """

    return json.dumps(_instance.power(base=base, exponent=exponent), default=str)
@mcp.tool()
@safe_tool
def square_root(number: float, precision: int) -> str:

    """Calculate the square root of a number with adjustable precision using the decimal module.

    Args:
        number (float): The number to calculate the square root of.
        precision (int): Desired precision for the result.

    Returns:
        result (float): The square root of the number, or an error message.
    """

    return json.dumps(

        _instance.square_root(number=number, precision=precision), default=str

    )
@mcp.tool()
@safe_tool
def absolute_value(number: float) -> str:

    """Calculate the absolute value of a number.

    Args:
        number (float): The number to calculate the absolute value of.

    Returns:
        result (float): The absolute value of the number.
    """

    return json.dumps(_instance.absolute_value(number=number), default=str)
@mcp.tool()
@safe_tool
def round_number(number: float, decimal_places: int = 0) -> str:

    """Round a number to a specified number of decimal places.

    Args:
        number (float): The number to round.
        decimal_places (int): [Optional] The number of decimal places to round to. Defaults to 0.

    Returns:
        result (float): The rounded number.
    """

    return json.dumps(

        _instance.round_number(number=number, decimal_places=decimal_places),

        default=str,

    )
@mcp.tool()
@safe_tool
def percentage(part: float, whole: float) -> str:

    """Calculate the percentage of a part relative to a whole.

    Args:
        part (float): The part value.
        whole (float): The whole value.

    Returns:
        result (float): The percentage of the part relative to the whole.
    """

    return json.dumps(_instance.percentage(part=part, whole=whole), default=str)
@mcp.tool()
@safe_tool
def min_value(numbers: List[float]) -> str:

    """Find the minimum value in a list of numbers.

    Args:
        numbers (List[float]): List of numbers to find the minimum from.

    Returns:
        result (float): The minimum value in the list.
    """

    return json.dumps(_instance.min_value(numbers=numbers), default=str)
@mcp.tool()
@safe_tool
def max_value(numbers: List[float]) -> str:

    """Find the maximum value in a list of numbers.

    Args:
        numbers (List[float]): List of numbers to find the maximum from.

    Returns:
        result (float): The maximum value in the list.
    """

    return json.dumps(_instance.max_value(numbers=numbers), default=str)
@mcp.tool()
@safe_tool
def sum_values(numbers: List[float]) -> str:

    """Calculate the sum of a list of numbers.

    Args:
        numbers (List[float]): List of numbers to sum.

    Returns:
        result (float): The sum of all numbers in the list.
    """

    return json.dumps(_instance.sum_values(numbers=numbers), default=str)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

