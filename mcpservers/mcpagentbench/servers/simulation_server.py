"""
MCPAgentBench Simulation MCP Server.
Concrete FastMCP server with 8 tools for the simulation domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from ast import Dict
from typing import List
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-simulation")
@mcp.tool()
@safe_tool
def create_object(object_type: str, name: str, location: list, size: list) -> str:

    '''```python
    """
    Creates a 3D object of specified type with given attributes.

    This function supports creating various types of 3D objects, including
    cubes, spheres, planes, birds, and custom objects. Each object is
    characterized by its type, name, location, and size, and may have
    additional properties based on its type.

    Args:
        object_type (str): The type of the 3D object to create. Must be one of
            'cube', 'sphere', 'plane', 'bird', or 'custom'.
        name (str): The name of the 3D object. Must be a non-empty string and
            unique among existing objects.
        location (list or tuple): The (x, y, z) coordinates specifying the
            object's location. Must be a list or tuple of three numbers.
        size (int, float, list, or tuple): The size of the object. Can be a
            single number or a list/tuple of dimensions.

    Returns:
        str: A confirmation message indicating successful creation of the 3D
        object with its name, type, location, and size.
    """
```'''

    if not hasattr(create_object, 'mock_db'):

        create_object.mock_db = {'objects': []}

    valid_types = {'cube', 'sphere', 'plane', 'bird', 'custom'}

    if not isinstance(object_type, str) or object_type.lower() not in valid_types:

        raise ValueError(f"Invalid object_type '{object_type}'. Must be one of {valid_types}.")

    if not isinstance(name, str) or not name.strip():

        raise ValueError('Invalid name. Name must be a non-empty string.')

    if not isinstance(location, (list, tuple)) or len(location) != 3 or (not all((isinstance(coord, (int, float)) for coord in location))):

        raise ValueError('Invalid location. Must be a list/tuple of three numbers (x, y, z).')

    if not isinstance(size, (int, float, list, tuple)):

        raise ValueError('Invalid size. Must be a number or list/tuple of dimensions.')

    if isinstance(size, (list, tuple)) and (not all((isinstance(s, (int, float)) for s in size))):

        raise ValueError('Invalid size dimensions. All elements must be numbers.')

    for obj in create_object.mock_db['objects']:

        if obj['name'].lower() == name.lower():

            raise ValueError(f"An object named '{name}' already exists.")

    obj_data = {'type': object_type.lower(), 'name': name, 'location': tuple(location), 'size': size, 'properties': {}}

    if object_type.lower() == 'bird':

        obj_data['properties'] = {'color': {'body': 'brown', 'wings': 'blue'}, 'behavior': {'flight_pattern': 'natural random', 'avoids_sun': True, 'speed_dynamic': True, 'sun_interaction': 'adjust trajectory to avoid sun proximity'}}

    elif object_type.lower() == 'cube':

        obj_data['properties'] = {'material': 'default', 'shading': 'smooth'}

    elif object_type.lower() == 'sphere':

        obj_data['properties'] = {'material': 'glossy', 'segments': 32}

    elif object_type.lower() == 'plane':

        obj_data['properties'] = {'material': 'matte', 'subdivisions': 1}

    else:

        obj_data['properties'] = {'material': 'custom', 'notes': 'Custom object created for special use'}

    create_object.mock_db['objects'].append(obj_data)

    return f"3D object '{name}' of type '{object_type}' created successfully at {location} with size {size}."
@mcp.tool()
@safe_tool
def modify_object(target_object: str, color: str, rotation: str, scale: str, animate: str) -> str:

    '''```python
    """
    Modifies the properties of a specified object within a scene.

    This function updates the color, rotation, scale, and animation state of the
    given object. If the object is a 'bird', natural flight safety adjustments are
    applied to ensure it maintains a safe distance from the 'sun' object based on
    its current location within the scene.

    Args:
        target_object (str): The name of the object to be modified.
        color (str): The new color of the object, formatted as 'R,G,B' (0-255)
        rotation (str): The new rotation of the object in the format 'x,y,z'.
        scale (str): The new scale of the object in the format 'x,y,z'.
        animate (str): The animation state, either 'true' or 'false'.

    Returns:
        str: A message indicating the success of the modification, with additional
        notes if natural flight adjustments were applied to a 'bird' object.
    """
```'''

    mock_scene_objects = {'bird': {'location': '0,0,10', 'rotation': '0,0,0', 'scale': '1,1,1', 'visible': 'true', 'color': '255,255,0', 'animate': 'true'}, 'sun': {'location': '50,200,300', 'rotation': '0,45,0', 'scale': '10,10,10', 'visible': 'true', 'color': '255,255,0', 'animate': 'false'}, 'tree': {'location': '10,20,0', 'rotation': '0,0,0', 'scale': '3,3,3', 'visible': 'true', 'color': '34,139,34', 'animate': 'false'}}

    for (param_target_object, param_value) in {'target_object': target_object, 'color': color, 'rotation': rotation, 'scale': scale, 'animate': animate}.items():

        if not isinstance(param_value, str) or not param_value.strip():

            raise ValueError(f"Invalid value for '{param_target_object}': must be a non-empty string.")

    if target_object not in mock_scene_objects:

        raise ValueError(f"Object '{target_object}' not found in the scene.")

    mock_scene_objects[target_object]['color'] = color

    mock_scene_objects[target_object]['rotation'] = rotation

    mock_scene_objects[target_object]['scale'] = scale

    mock_scene_objects[target_object]['animate'] = animate

    mock_scene_objects[target_object]['visible'] = 'true' if animate.lower() == 'true' else 'false'

    if target_object == 'bird':

        sun_loc = [float(c) for c in mock_scene_objects['sun']['location'].split(',')]

        bird_loc = [float(c) for c in mock_scene_objects['bird']['location'].split(',')]

        distance_to_sun = ((bird_loc[0] - sun_loc[0]) ** 2 + (bird_loc[1] - sun_loc[1]) ** 2) ** 0.5

        if distance_to_sun < 50:

            bird_loc[0] += 10

            new_location = ','.join(map(str, bird_loc))

            mock_scene_objects[target_object]['location'] = new_location

        adaptation_note = " Bird's flight speed adapted to avoid sun proximity."

        return f"Object '{target_object}' modified successfully with natural flight adjustments.{adaptation_note}"

    return f"Object '{target_object}' modified successfully."
@mcp.tool()
@safe_tool
def create_physics_scene(objects: List[dict], floor: bool, gravity: str, scene_name: str) -> str:

    '''```python
    """
    Creates a physics scene with configurable parameters.

    This function initializes a physics scene using the specified objects,
    floor presence, gravity vector, and scene name. The scene is set up
    with a mock physics engine and is intended for simulations such as
    robot obstacle avoidance.

    Args:
        objects (list of dict): A non-empty list of object definitions,
            where each object is a dictionary containing:
            - 'type' (str): The type of the object.
            - 'position' (list of float): A list of three coordinates
              representing the object's position in 3D space.
        floor (bool): A boolean indicating whether a floor should be
            included in the scene.
        gravity (str): A string representing the gravity vector in the
            format '[x, y, z]'. For example, '[0, -0.981, 0]'.
        scene_name (str): A non-empty string representing the name of
            the scene.

    Returns:
        str: A message indicating successful creation of the physics
        scene, including the scene name, number of objects, and gravity
        vector.
    """
```'''

    mock_physics_scenes_db = getattr(create_physics_scene, '_mock_db', {})

    if not isinstance(objects, list) or len(objects) == 0:

        raise ValueError('`objects` must be a non-empty list of object definitions (dicts with type and position).')

    if not isinstance(floor, bool):

        raise ValueError('`floor` must be a boolean value.')

    if not isinstance(gravity, str):

        raise ValueError("`gravity` must be a string representing a vector, e.g., '[0, -0.981, 0]'.")

    if not isinstance(scene_name, str) or not scene_name.strip():

        raise ValueError('`scene_name` must be a non-empty string.')

    try:

        gravity_vector = eval(gravity) if gravity.strip().startswith('[') else [0, -0.981, 0]

        if not (isinstance(gravity_vector, list) and len(gravity_vector) == 3):

            raise ValueError

    except Exception:

        raise ValueError("`gravity` must be a string representing a 3D vector, e.g., '[0, -0.981, 0]'.")

    validated_objects = []

    for obj in objects:

        if not isinstance(obj, dict) or 'type' not in obj or 'position' not in obj:

            raise ValueError("Each object must be a dict with 'type' and 'position'.")

        if not isinstance(obj['type'], str):

            raise ValueError("Object 'type' must be a string.")

        if not (isinstance(obj['position'], list) and len(obj['position']) == 3):

            raise ValueError("Object 'position' must be a list of 3 coordinates.")

        validated_objects.append(obj)

    scene_data = {'name': scene_name, 'gravity': gravity_vector, 'floor': floor, 'objects': validated_objects, 'engine': 'MockPhysicsEngine v1.0', 'status': 'initialized', 'metadata': {'created_for': 'robot_obstacle_avoidance_simulation', 'supports_autonomous_decision_making': True, 'integrated_with': ['MATLAB', 'Java Simulation Software']}}

    mock_physics_scenes_db[scene_name] = scene_data

    setattr(create_physics_scene, '_mock_db', mock_physics_scenes_db)

    return f"Physics scene '{scene_name}' created successfully with {len(validated_objects)} objects and gravity {gravity_vector}."
@mcp.tool()
@safe_tool
def create_robot(robot_type: str, position: str) -> str:

    '''```python
    """
    Creates a robot in the scene at a specified position.

    This function initializes a robot of the given type at the provided
    coordinates within the simulation scene. The robot is assigned a unique
    identifier and its capabilities are set based on the specified type.

    Args:
        robot_type (str): The type of robot to create. Could be 'franka', 'jetbot', 'carter', 'g1', or 'go1'.
        position (str): The position in the scene where the robot should be
            placed. Must be a string in the format '[x, y, z]' with numeric
            values representing the coordinates.

    Returns:
        str: A confirmation message including the robot type, unique ID, and
        position. Additional context notes are provided based on the robot type.
    """
```'''

    scene_state = {'robots': []}

    robot_capabilities = {'franka': {'description': 'Franka Emika Panda robotic arm, used for precise manipulation tasks', 'capabilities': ['pick_and_place', 'object_detection', 'MATLAB_integration']}, 'jetbot': {'description': 'NVIDIA JetBot small mobile robot with AI capabilities', 'capabilities': ['obstacle_avoidance', 'path_planning', 'camera_vision']}, 'carter': {'description': 'Carter mobile robot for research and indoor navigation', 'capabilities': ['LIDAR_navigation', 'autonomous_mapping', 'physics_simulation']}, 'g1': {'description': 'Humanoid robot G1 for advanced decision-making simulations', 'capabilities': ['autonomous_decision_making', 'speech_recognition', 'complex_behavior_sim']}, 'go1': {'description': 'Unitree Go1 quadruped robot for dynamic movement and terrain navigation', 'capabilities': ['terrain_navigation', 'dynamic_balance', 'obstacle_avoidance']}}

    if robot_type not in robot_capabilities:

        raise ValueError(f"Invalid robot_type '{robot_type}'. Must be one of: {', '.join(robot_capabilities.keys())}")

    import ast

    try:

        pos_list = ast.literal_eval(position)

        if not isinstance(pos_list, (list, tuple)) or len(pos_list) != 3 or (not all((isinstance(coord, (int, float)) for coord in pos_list))):

            raise ValueError

    except Exception:

        raise ValueError("Invalid position format. Must be a string in the format '[x, y, z]' with numeric values.")

    import uuid

    robot_id = str(uuid.uuid4())

    new_robot = {'id': robot_id, 'type': robot_type, 'position': pos_list, 'description': robot_capabilities[robot_type]['description'], 'capabilities': robot_capabilities[robot_type]['capabilities'], 'status': 'idle'}

    scene_state['robots'].append(new_robot)

    if robot_type == 'franka':

        context_note = 'This robot can be integrated with MATLAB for object detection tasks.'

    elif robot_type in ['carter', 'g1']:

        context_note = 'This robot is suitable for Java-based physics simulations and autonomous behavior research.'

    elif robot_type == 'jetbot':

        context_note = 'This robot is ideal for implementing and testing obstacle avoidance algorithms.'

    elif robot_type == 'go1':

        context_note = 'This quadruped robot can navigate complex terrains in simulation.'

    else:

        context_note = ''

    return f"Robot '{robot_type}' created with ID {robot_id} at position {pos_list}. {context_note}"
@mcp.tool()
@safe_tool
def generate_3d_assets(player_bio: str, num_assets: str) -> str:

    '''```python
    """
    Generates 3D assets for video game scene composition based on a player's bio.

    This function creates a collection of 3D assets tailored to the player's
    specified bio, which can be used for enhancing video game environments.
    The assets are returned as a JSON string containing prompts and GLB file data.

    Args:
        player_bio (str): A non-empty string representing the player's bio,
            which influences the type of 3D assets generated. Should be in the form of xxx style.
        num_assets (str): A string representing a positive integer that specifies
            the number of 3D assets to generate.

    Returns:
        str: A JSON string containing the player's bio, the number of requested
        assets, and a list of generated assets with their prompts and GLB file data.

    Raises:
        ValueError: If `player_bio` is not a non-empty string.
        ValueError: If `num_assets` is not a string representing a positive integer.
    """
```'''

    mock_asset_db = {'battle_royal': [{'prompt': 'Generate a ruined cityscape with destructible buildings for intense battle scenes', 'glb_data': '<GLB_FILE_DATA_RUINED_CITY_BASE64>'}, {'prompt': 'Create a dense jungle arena with hidden bunkers and sniper towers', 'glb_data': '<GLB_FILE_DATA_JUNGLE_ARENA_BASE64>'}, {'prompt': 'Design a futuristic battle arena with forcefields and holographic billboards', 'glb_data': '<GLB_FILE_DATA_FUTURISTIC_ARENA_BASE64>'}, {'prompt': 'Produce an abandoned industrial complex with multiple entry points and cover spots', 'glb_data': '<GLB_FILE_DATA_INDUSTRIAL_COMPLEX_BASE64>'}], 'fantasy_warrior': [{'prompt': 'Generate a medieval castle courtyard with armory and training grounds', 'glb_data': '<GLB_FILE_DATA_CASTLE_COURTYARD_BASE64>'}, {'prompt': 'Create an enchanted forest battleground with mystical lighting', 'glb_data': '<GLB_FILE_DATA_ENCHANTED_FOREST_BASE64>'}], 'space_marine': [{'prompt': 'Generate a space station docking bay with battle damage', 'glb_data': '<GLB_FILE_DATA_SPACE_STATION_BASE64>'}, {'prompt': 'Create an alien planet surface with volcanic terrain and hostile structures', 'glb_data': '<GLB_FILE_DATA_ALIEN_PLANET_BASE64>'}]}

    import json

    if not isinstance(player_bio, str) or not player_bio.strip():

        raise ValueError('player_bio must be a non-empty string.')

    if not isinstance(num_assets, str) or not num_assets.isdigit():

        raise ValueError('num_assets must be a string representing a positive integer.')

    num_assets_int = int(num_assets)

    if num_assets_int <= 0:

        raise ValueError('num_assets must be greater than 0.')

    bio_key = player_bio.strip().lower().replace(' ', '_')

    if bio_key not in mock_asset_db:

        mock_assets = [{'prompt': f'Generate a generic open field battleground for {player_bio}', 'glb_data': '<GLB_FILE_DATA_GENERIC_FIELD_BASE64>'}, {'prompt': f'Create a small urban combat zone adapted to {player_bio} style', 'glb_data': '<GLB_FILE_DATA_GENERIC_URBAN_BASE64>'}]

    else:

        mock_assets = mock_asset_db[bio_key]

    generated_assets = []

    while len(generated_assets) < num_assets_int:

        generated_assets.extend(mock_assets)

    generated_assets = generated_assets[:num_assets_int]

    response = {'player_bio': player_bio, 'requested_assets': num_assets_int, 'generated_assets': generated_assets}

    return json.dumps(response)
@mcp.tool()
@safe_tool
def get_scene_info(scene_name: str) -> str:

    '''```python
    """
    Retrieve information about a specified SketchUp scene.

    This function fetches details about a given scene within a SketchUp project.
    The scene information includes environment settings, lighting conditions,
    weather, objects present in the scene, and camera configuration.

    Args:
        scene_name (str): The name of the scene to retrieve information for.
                          Must be a non-empty string.

    Returns:
        str: A formatted string containing the scene information in JSON format.
             If the scene is not found or an error occurs, an error message is returned.
    """
```'''

    mock_scenes_db = {'SkyView': {'environment': 'outdoor', 'sun_position': {'azimuth': 135.0, 'altitude': 45.0}, 'lighting': 'daylight', 'weather': 'clear', 'objects': [{'name': 'bird_01', 'type': 'animal', 'appearance': {'body_color': 'brown', 'wing_color': 'blue'}, 'behavior': {'flight_pattern': 'random', 'interaction': 'avoids_sun', 'speed_mode': 'dynamic'}}, {'name': 'tree_cluster', 'type': 'vegetation', 'species': 'oak', 'count': 12}], 'camera': {'position': [0, 0, 10], 'target': [50, 50, 0], 'fov': 60}}, 'InteriorRoom': {'environment': 'indoor', 'lighting': 'artificial', 'weather': None, 'objects': [{'name': 'desk', 'type': 'furniture', 'material': 'wood'}], 'camera': {'position': [2, 1.5, 1.7], 'target': [0, 0, 0], 'fov': 45}}}

    if not isinstance(scene_name, str) or not scene_name.strip():

        return "Error: 'scene_name' must be a non-empty string."

    scene_data = mock_scenes_db.get(scene_name)

    if not scene_data:

        return f"Error: Scene '{scene_name}' not found in the SketchUp project."

    import json

    try:

        scene_info_str = json.dumps(scene_data, indent=2)

    except (TypeError, ValueError) as e:

        return f'Error: Failed to serialize scene data. Details: {str(e)}'

    return f"Scene Information for '{scene_name}':\n{scene_info_str}"
@mcp.tool()
@safe_tool
def detect_objects(image_path: str) -> str:

    '''```python
    """
    Performs object detection on a given image to identify and localize objects of interest.

    This function processes an input image specified by its file path, detecting objects such as
    people, vehicles, or items. It returns details including bounding boxes, object classes, and
    confidence scores for each detected object. These outputs can be used for further analysis,
    such as cropping regions of interest.

    Args:
        image_path (str): The file path to the input image. Must be a non-empty string.

    Returns:
        str: A formatted string listing detected objects with their bounding boxes, classes,
        and confidence scores. The bounding box coordinates are provided as [x_left, y_top, x_right, y_bottom]
        where (x_left, y_top) is the top-left corner and (x_right, y_bottom) is the bottom-right corner.
        If no objects are detected or the image path is unknown, an appropriate message is returned.
    """
```'''

    mock_detection_db = {'street_scene_people.jpg': [{'bbox': [50, 80, 180, 400], 'class': 'person', 'confidence': 0.95}, {'bbox': [220, 60, 350, 390], 'class': 'person', 'confidence': 0.92}, {'bbox': [400, 100, 520, 420], 'class': 'person', 'confidence': 0.88}]}

    if not isinstance(image_path, str) or not image_path.strip():

        return "Error: 'image_path' must be a non-empty string."

    detections = mock_detection_db.get(image_path)

    if detections is None:

        return f"No objects detected or unknown image for path '{image_path}'."

    output_lines = ['Detected objects:']

    for det in detections:

        bbox_str = f"bbox={det['bbox']}"

        class_str = f"class='{det['class']}'"

        conf_str = f"confidence={det['confidence']:.2f}"

        output_lines.append(f' - {class_str}, {bbox_str}, {conf_str}')

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def estimate_pose(object_regions: list) -> str:

    '''```python
    """
    Estimates human poses within specified person regions derived from a previous object detection step.

    This function processes a list of bounding boxes, each representing a detected person,
    and returns a JSON string detailing the estimated body keypoints and their confidence scores.
    Keypoints include head, shoulders, elbows, wrists, hips, knees, and ankles, enabling
    analysis of individual postures and actions in scenes with multiple people.

    Args:
        object_regions (list): A list of dictionaries, where each dictionary specifies a person's
                               bounding box with the following keys:
                               - x (int): X coordinate of the top-left corner of the bounding box.
                               - y (int): Y coordinate of the top-left corner of the bounding box.
                               - width (int): Width of the bounding box in pixels.
                               - height (int): Height of the bounding box in pixels.
                               Example: [{"x": 50, "y": 80, "width": 130, "height": 320}, ...]

    Returns:
        str: A JSON-formatted string containing pose estimation results. Each result includes
             body keypoints and their confidence scores for each person region, facilitating
             posture and action analysis in multi-person scenarios.
    """
```'''

    mock_pose_db = {(50, 80, 130, 320): [{'part': 'head', 'x': 115, 'y': 90, 'confidence': 0.98}, {'part': 'left_shoulder', 'x': 95, 'y': 140, 'confidence': 0.95}, {'part': 'right_shoulder', 'x': 135, 'y': 140, 'confidence': 0.96}, {'part': 'left_elbow', 'x': 85, 'y': 190, 'confidence': 0.93}, {'part': 'right_elbow', 'x': 145, 'y': 190, 'confidence': 0.92}, {'part': 'left_wrist', 'x': 75, 'y': 240, 'confidence': 0.9}, {'part': 'right_wrist', 'x': 155, 'y': 240, 'confidence': 0.89}, {'part': 'left_hip', 'x': 105, 'y': 260, 'confidence': 0.94}, {'part': 'right_hip', 'x': 125, 'y': 260, 'confidence': 0.93}, {'part': 'left_knee', 'x': 105, 'y': 320, 'confidence': 0.91}, {'part': 'right_knee', 'x': 125, 'y': 320, 'confidence': 0.9}, {'part': 'left_ankle', 'x': 105, 'y': 380, 'confidence': 0.88}, {'part': 'right_ankle', 'x': 125, 'y': 380, 'confidence': 0.87}], (220, 60, 130, 330): [{'part': 'head', 'x': 285, 'y': 70, 'confidence': 0.97}, {'part': 'left_shoulder', 'x': 265, 'y': 120, 'confidence': 0.94}, {'part': 'right_shoulder', 'x': 305, 'y': 120, 'confidence': 0.95}, {'part': 'left_elbow', 'x': 255, 'y': 170, 'confidence': 0.92}, {'part': 'right_elbow', 'x': 315, 'y': 170, 'confidence': 0.91}, {'part': 'left_wrist', 'x': 245, 'y': 220, 'confidence': 0.89}, {'part': 'right_wrist', 'x': 325, 'y': 220, 'confidence': 0.88}, {'part': 'left_hip', 'x': 275, 'y': 240, 'confidence': 0.93}, {'part': 'right_hip', 'x': 295, 'y': 240, 'confidence': 0.92}, {'part': 'left_knee', 'x': 275, 'y': 300, 'confidence': 0.9}, {'part': 'right_knee', 'x': 295, 'y': 300, 'confidence': 0.89}, {'part': 'left_ankle', 'x': 275, 'y': 360, 'confidence': 0.87}, {'part': 'right_ankle', 'x': 295, 'y': 360, 'confidence': 0.86}], (400, 100, 120, 320): [{'part': 'head', 'x': 460, 'y': 110, 'confidence': 0.96}, {'part': 'left_shoulder', 'x': 440, 'y': 160, 'confidence': 0.93}, {'part': 'right_shoulder', 'x': 480, 'y': 160, 'confidence': 0.94}, {'part': 'left_elbow', 'x': 430, 'y': 210, 'confidence': 0.91}, {'part': 'right_elbow', 'x': 490, 'y': 210, 'confidence': 0.9}, {'part': 'left_wrist', 'x': 420, 'y': 260, 'confidence': 0.88}, {'part': 'right_wrist', 'x': 500, 'y': 260, 'confidence': 0.87}, {'part': 'left_hip', 'x': 450, 'y': 280, 'confidence': 0.92}, {'part': 'right_hip', 'x': 470, 'y': 280, 'confidence': 0.91}, {'part': 'left_knee', 'x': 450, 'y': 340, 'confidence': 0.89}, {'part': 'right_knee', 'x': 470, 'y': 340, 'confidence': 0.88}, {'part': 'left_ankle', 'x': 450, 'y': 400, 'confidence': 0.86}, {'part': 'right_ankle', 'x': 470, 'y': 400, 'confidence': 0.85}]}

    if not isinstance(object_regions, list):

        raise ValueError('object_regions must be a list of bounding boxes or cropped image references.')

    results = []

    for region in object_regions:

        if isinstance(region, dict) and all((k in region for k in ('x', 'y', 'width', 'height'))):

            bbox_tuple = (region['x'], region['y'], region['width'], region['height'])

            if bbox_tuple in mock_pose_db:

                results.append({'region': region, 'keypoints': mock_pose_db[bbox_tuple]})

            else:

                simulated_keypoints = [{'part': 'head', 'x': region['x'] + region['width'] // 2, 'y': region['y'] + 10, 'confidence': 0.85}, {'part': 'left_shoulder', 'x': region['x'] + region['width'] // 3, 'y': region['y'] + 50, 'confidence': 0.8}, {'part': 'right_shoulder', 'x': region['x'] + 2 * region['width'] // 3, 'y': region['y'] + 50, 'confidence': 0.81}]

                results.append({'region': region, 'keypoints': simulated_keypoints})

        else:

            raise ValueError('Each region must be a dict with x, y, width, height keys representing bounding box.')

    import json

    return json.dumps({'pose_estimations': results}, indent=2)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

