"""
BFCL Vehicle MCP Server.
Wraps the VehicleControlAPI class as MCP tools for the BFCL benchmark.
"""
import json
from typing import Dict, List, Union
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.vehicle_control import VehicleControlAPI
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-vehicle")
_instance = VehicleControlAPI()
@mcp.tool()
@safe_tool
def activateParkingBrake(mode: str) -> Dict[str, Union[str, float]]:

    """
    Activates the parking brake of the vehicle.

    Args:
        mode (str): The mode to set. [Enum]: ["engage", "release"]
    Returns:
        parkingBrakeStatus (str): The status of the brake. [Enum]: ["engaged", "released"]
        _parkingBrakeForce (float): The force applied to the brake in Newtons.
        _slopeAngle (float): The slope angle in degrees.
    """

    return _instance.activateParkingBrake(mode=mode)
@mcp.tool()
@safe_tool
def adjustClimateControl(

    temperature: float,

    unit: str = "celsius",

    fanSpeed: int = 50,

    mode: str = "auto",
) -> Dict[str, Union[str, float]]:

    """
    Adjusts the climate control of the vehicle.

    Args:
        temperature (float): The temperature to set in degree. Default to be celsius.
        unit (str): [Optional] The unit of temperature. [Enum]: ["celsius", "fahrenheit"]
        fanSpeed (int): [Optional] The fan speed to set from 0 to 100. Default is 50.
        mode (str): [Optional] The climate mode to set. [Enum]: ["auto", "cool", "heat", "defrost"]
    Returns:
        currentTemperature (float): The current temperature set in degree Celsius.
        climateMode (str): The current climate mode set.
        humidityLevel (float): The humidity level in percentage.
    """

    return _instance.adjustClimateControl(

        temperature=temperature, unit=unit, fanSpeed=fanSpeed, mode=mode

    )
@mcp.tool()
@safe_tool
def check_tire_pressure() -> Dict:

    """
    Checks the tire pressure of the vehicle.

    Returns:
        tirePressure (Dict): The tire pressure of the vehicle.
            - frontLeftTirePressure (float): The pressure of the front left tire in psi.
            - frontRightTirePressure (float): The pressure of the front right tire in psi.
            - rearLeftTirePressure (float): The pressure of the rear left tire in psi.
            - rearRightTirePressure (float): The pressure of the rear right tire in psi.
            - healthy_tire_pressure (bool): True if the tire pressure is healthy, False otherwise.
            - car_info (Dict): The metadata of the car.
    """

    return _instance.check_tire_pressure()
@mcp.tool()
@safe_tool
def displayCarStatus(option: str) -> Dict[str, Union[str, float, Dict[str, str]]]:

    """
    Displays the status of the vehicle based on the provided display option.

    Args:
        option (str): The option to display. [Enum]: ["fuel", "battery", "doors", "climate", "headlights", "parkingBrake", "brakePedal", "engine"]
    Returns:
        status (Dict): The status of the vehicle based on the option.
    """

    return _instance.displayCarStatus(option=option)
@mcp.tool()
@safe_tool
def display_log(messages: List[str]) -> Dict[str, List[str]]:

    """
    Displays the log messages.

    Args:
        messages (List[str]): The list of messages to display.
    Returns:
        log (List[str]): The list of messages displayed.
    """

    return _instance.display_log(messages=messages)
@mcp.tool()
@safe_tool
def estimate_distance(cityA: str, cityB: str) -> Dict[str, float]:

    """
    Estimates the distance between two cities.

    Args:
        cityA (str): The zipcode of the first city.
        cityB (str): The zipcode of the second city.
    Returns:
        distance (float): The distance between the two cities in km.
        intermediaryCities (List[str]): [Optional] The list of intermediary cities between the two cities.
    """

    return _instance.estimate_distance(cityA=cityA, cityB=cityB)
@mcp.tool()
@safe_tool
def estimate_drive_feasibility_by_mileage(distance: float) -> Dict[str, bool]:

    """
    Estimates the milage of the vehicle given the distance needed to drive.

    Args:
        distance (float): The distance to travel in miles.
    Returns:
        canDrive (bool): True if the vehicle can drive the distance, False otherwise.
    """

    return _instance.estimate_drive_feasibility_by_mileage(distance=distance)
@mcp.tool()
@safe_tool
def fillFuelTank(fuelAmount: float) -> Dict[str, Union[str, float]]:

    """
    Fills the fuel tank of the vehicle. The fuel tank can hold up to 50 gallons.

    Args:
        fuelAmount (float): The amount of fuel to fill in gallons; this is the additional fuel to add to the tank.
    Returns:
        fuelLevel (float): The fuel level of the vehicle in gallons.
    """

    return _instance.fillFuelTank(fuelAmount=fuelAmount)
@mcp.tool()
@safe_tool
def find_nearest_tire_shop() -> Dict[str, str]:

    """
    Finds the nearest tire shop.

    Returns:
        shopLocation (str): The location of the nearest tire shop.
    """

    return _instance.find_nearest_tire_shop()
@mcp.tool()
@safe_tool
def gallon_to_liter(gallon: float) -> Dict[str, float]:

    """
    Converts the gallon to liter.

    Args:
        gallon (float): The amount of gallon to convert.
    Returns:
        liter (float): The amount of liter converted.
    """

    return _instance.gallon_to_liter(gallon=gallon)
@mcp.tool()
@safe_tool
def get_current_speed() -> Dict[str, float]:

    """
    Gets the current speed of the vehicle.

    Returns:
        currentSpeed (float): The current speed of the vehicle in km/h.
    """

    return _instance.get_current_speed()
@mcp.tool()
@safe_tool
def get_outside_temperature_from_google() -> Dict[str, float]:

    """
    Gets the outside temperature.

    Returns:
        outsideTemperature (float): The outside temperature in degree Celsius.
    """

    return _instance.get_outside_temperature_from_google()
@mcp.tool()
@safe_tool
def get_outside_temperature_from_weather_com() -> Dict[str, float]:

    """
    Gets the outside temperature.

    Returns:
        outsideTemperature (float): The outside temperature in degree Celsius.
    """

    return _instance.get_outside_temperature_from_weather_com()
@mcp.tool()
@safe_tool
def get_zipcode_based_on_city(city: str) -> Dict[str, str]:

    """
    Gets the zipcode based on the city.

    Args:
        city (str): The name of the city.
    Returns:
        zipcode (str): The zipcode of the city.
    """

    return _instance.get_zipcode_based_on_city(city=city)
@mcp.tool()
@safe_tool
def liter_to_gallon(liter: float) -> Dict[str, float]:

    """
    Converts the liter to gallon.

    Args:
        liter (float): The amount of liter to convert.
    Returns:
        gallon (float): The amount of gallon converted.
    """

    return _instance.liter_to_gallon(liter=liter)
@mcp.tool()
@safe_tool
def lockDoors(unlock: bool, door: list[str]) -> Dict[str, Union[str, int]]:

    """
    Locks the doors of the vehicle.

    Args:
        unlock (bool): True if the doors are to be unlocked, False otherwise.
        door (List[str]): The list of doors to lock or unlock. [Enum]: ["driver", "passenger", "rear_left", "rear_right"]
    Returns:
        lockStatus (str): The status of the lock. [Enum]: ["locked", "unlocked"]
        remainingUnlockedDoors (int): The number of remaining unlocked doors.
    """

    return _instance.lockDoors(unlock=unlock, door=door)
@mcp.tool()
@safe_tool
def pressBrakePedal(pedalPosition: float) -> Dict[str, Union[str, float]]:

    """
    Presses the brake pedal based on pedal position. The brake pedal will be kept pressed until released.

    Args:
        pedalPosition (float): Position of the brake pedal, between 0 (not pressed) and 1 (fully pressed).
    Returns:
        brakePedalStatus (str): The status of the brake pedal. [Enum]: ["pressed", "released"]
        brakePedalForce (float): The force applied to the brake pedal in Newtons.
    """

    return _instance.pressBrakePedal(pedalPosition=pedalPosition)
@mcp.tool()
@safe_tool
def releaseBrakePedal() -> Dict[str, Union[str, float]]:

    """
    Releases the brake pedal of the vehicle.

    Returns:
        brakePedalStatus (str): The status of the brake pedal. [Enum]: ["pressed", "released"]
        brakePedalForce (float): The force applied to the brake pedal in Newtons.
    """

    return _instance.releaseBrakePedal()
@mcp.tool()
@safe_tool
def setCruiseControl(

    speed: float, activate: bool, distanceToNextVehicle: float
) -> Dict[str, Union[str, float]]:

    """
    Sets the cruise control of the vehicle.

    Args:
        speed (float): The speed to set in m/h. The speed should be between 0 and 120 and a multiple of 5.
        activate (bool): True to activate the cruise control, False to deactivate.
        distanceToNextVehicle (float): The distance to the next vehicle in meters.
    Returns:
        cruiseStatus (str): The status of the cruise control. [Enum]: ["active", "inactive"]
        currentSpeed (float): The current speed of the vehicle in km/h.
        distanceToNextVehicle (float): The distance to the next vehicle in meters.
    """

    return _instance.setCruiseControl(

        speed=speed, activate=activate, distanceToNextVehicle=distanceToNextVehicle

    )
@mcp.tool()
@safe_tool
def setHeadlights(mode: str) -> Dict[str, str]:

    """
    Sets the headlights of the vehicle.

    Args:
        mode (str): The mode of the headlights. [Enum]: ["on", "off", "auto"]
    Returns:
        headlightStatus (str): The status of the headlights. [Enum]: ["on", "off"]
    """

    return _instance.setHeadlights(mode=mode)
@mcp.tool()
@safe_tool
def set_navigation(destination: str) -> Dict[str, str]:

    """
    Navigates to the destination.

    Args:
        destination (str): The destination to navigate in the format of street, city, state.
    Returns:
        status (str): The status of the navigation.
    """

    return _instance.set_navigation(destination=destination)
@mcp.tool()
@safe_tool
def startEngine(ignitionMode: str) -> Dict[str, Union[str, float]]:

    """
    Starts the engine of the vehicle.

    Args:
        ignitionMode (str): The ignition mode of the vehicle. [Enum]: ["START", "STOP"]
    Returns:
        engineState (str): The state of the engine. [Enum]: ["running", "stopped"]
        fuelLevel (float): The fuel level of the vehicle in gallons.
        batteryVoltage (float): The battery voltage of the vehicle in volts.
    """

    return _instance.startEngine(ignitionMode=ignitionMode)
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """
    Load a scenario configuration into the vehicle control system.

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
    Get the current state of the vehicle control system.

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

