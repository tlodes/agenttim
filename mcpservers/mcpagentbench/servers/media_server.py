"""
MCPAgentBench Media MCP Server.
Concrete FastMCP server with 8 tools for the media domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-media")
@mcp.tool()
@safe_tool
def AudioEditor_apply_fades(audio_file: str, fade_in_ms: str, fade_out_ms: str) -> str:

    '''```python
    """
    Applies fade-in and fade-out effects to an audio file and saves the processed file.

    This function processes an audio file by applying specified fade-in and fade-out
    effects, measured in milliseconds. The processed audio file is saved in the
    './outputs/audio_processed/' directory with a modified filename indicating the
    applied effects.

    Args:
        audio_file (str): The path to the audio file to be processed. Must be a
            non-empty string.
        fade_in_ms (str): The duration of the fade-in effect in milliseconds. Must
            be a non-negative integer represented as a string.
        fade_out_ms (str): The duration of the fade-out effect in milliseconds. Must
            be a non-negative integer represented as a string.

    Returns:
        str: A success message confirming the applied fade effects and the location
        where the processed audio file is saved. If input validation fails, an error
        message is returned.
    """
```'''

    if not isinstance(audio_file, str) or not audio_file.strip():

        return "Error: 'audio_file' must be a non-empty string."

    try:

        fade_in_ms_val = int(fade_in_ms)

        fade_out_ms_val = int(fade_out_ms)

    except ValueError:

        return "Error: 'fade_in_ms' and 'fade_out_ms' must be integers (milliseconds)."

    if fade_in_ms_val < 0 or fade_out_ms_val < 0:

        return 'Error: Fade durations cannot be negative.'

    import os

    base_name = os.path.splitext(os.path.basename(audio_file))[0]

    output_path = f'./outputs/audio_processed/{base_name}_faded.mp3'

    fade_effects = []

    if fade_in_ms_val > 0:

        fade_effects.append(f'fade-in: {fade_in_ms_val}ms')

    if fade_out_ms_val > 0:

        fade_effects.append(f'fade-out: {fade_out_ms_val}ms')

    if not fade_effects:

        fade_description = 'No fade effects applied'

    else:

        fade_description = 'Applied ' + ' and '.join(fade_effects)

    return f'Audio fade effects applied successfully. {fade_description}. Processed audio saved to: {output_path}'
@mcp.tool()
@safe_tool
def AudioEditor_apply_speed_adjustment(audio_file: str, speed_factor: str) -> str:

    '''```python
    """
    Adjusts the playback speed and pitch of an audio file.

    This function loads an audio file and modifies its playback speed based on
    the specified speed factor. The speed adjustment affects both the duration
    and pitch of the audio: increasing the speed raises the pitch and shortens
    the duration, while decreasing the speed lowers the pitch and lengthens the
    duration.

    Args:
        audio_file (str): The path to the audio file to be processed.
        speed_factor (str): The factor by which to adjust the speed. Values greater
            than 1.0 increase speed and pitch, reducing duration; values less than
            1.0 decrease speed and pitch, increasing duration. Common values include
            0.5 (half speed), 1.25 (25% faster), and 2.0 (double speed). Extreme values
            (< 0.25 or > 4.0) may result in poor audio quality.

    Returns:
        tuple: A tuple containing:
            - (sample_rate: int, speed_adjusted_audio_data: array): The sample rate and
              adjusted audio data, or None if an error occurred.
            - str: A status message indicating the speed factor applied, the change in
              duration, or error information.

    Note:
        For pitch-preserving speed changes, consider using time-stretching techniques.
        The function preserves the original sample rate but alters the audio duration.
    """
```'''

    mock_audio_db = {'url/to/audio.mp3': {'title': 'Dance Song Original', 'sample_rate': 44100, 'duration_seconds': 240, 'data': [0.1, 0.2, -0.1, -0.2] * 1000}, 'url/to/demo_song.mp3': {'title': 'Producer Demo Track', 'sample_rate': 48000, 'duration_seconds': 180, 'data': [0.05, 0.1, -0.05, -0.1] * 1200}}

    try:

        if not isinstance(audio_file, str) or audio_file.strip() == '':

            return (None, 'Error: Invalid audio_file path.')

        try:

            speed_factor_val = float(speed_factor)

        except ValueError:

            return (None, 'Error: speed_factor must be a numeric value.')

        if speed_factor_val <= 0:

            return (None, 'Error: speed_factor must be greater than 0.')

        if audio_file not in mock_audio_db:

            return (None, f"Error: Audio file '{audio_file}' not found in the system.")

        audio_info = mock_audio_db[audio_file]

        original_duration = audio_info['duration_seconds']

        sample_rate = audio_info['sample_rate']

        audio_data = audio_info['data']

        new_duration = original_duration / speed_factor_val

        adjusted_length = max(1, int(len(audio_data) / speed_factor_val))

        adjusted_audio_data = audio_data[:adjusted_length]

        if speed_factor_val > 1.0:

            effect_desc = 'increased speed and pitch (shorter duration)'

        elif speed_factor_val < 1.0:

            effect_desc = 'decreased speed and pitch (longer duration)'

        else:

            effect_desc = 'no change in speed or pitch'

        status_msg = f"Applied speed factor {speed_factor_val:.2f} to '{audio_info['title']}'. Original duration: {original_duration:.2f} sec, New duration: {new_duration:.2f} sec. Effect: {effect_desc}."

        return str(((sample_rate, adjusted_audio_data), status_msg))

    except Exception as e:

        return str((None, f'Unexpected error occurred: {str(e)}'))
@mcp.tool()
@safe_tool
def AudioEditor_apply_volume_adjustment(audio_file: str, volume_adjustment: str) -> str:

    '''```python
    """
    Adjusts the volume of an audio file by applying a specified gain in decibels.

    This function modifies the audio file's volume based on the provided gain value,
    which is specified in decibels. Positive values increase the volume, while negative
    values decrease it.

    Args:
        audio_file (str): The file path to the audio file that will be processed.
                          Must be a non-empty string.
        volume_adjustment (str): The gain adjustment in decibels. This should be a
                                 string representing a numeric value (e.g., "3.0" for
                                 +3dB, "-2.0" for -2dB).

    Returns:
        str: A success message indicating the completion of the volume adjustment
             operation, including the applied gain value.
    """
```'''

    if not isinstance(audio_file, str) or not audio_file.strip():

        return "Error: 'audio_file' must be a non-empty string."

    try:

        volume_adjustment_val = float(volume_adjustment)

    except ValueError:

        return "Error: 'volume_adjustment' must be a numeric value."

    return f'Volume adjustment operation completed successfully. Applied {volume_adjustment_val:+.1f} dB gain to audio file.'
@mcp.tool()
@safe_tool
def AudioEditor_process_cut_audio(audio_file: str, start_time: str, end_time: str) -> str:

    '''```python
"""
Cuts an audio file to extract a segment from a specified start time to end time.
This function takes an audio file along with start and end times in seconds, then extracts the
segment beginning at the start time and ending at the end time. The output is saved as a new
audio file.
Args:
    audio_file (str): The file path to the audio file to be processed. It must be a non-empty string.
    start_time (str): The start time for the audio cut in seconds, represented as a string
                      (e.g., "10.5" for 10.5 seconds). It must be a non-negative numeric value.
    end_time (str):   The end time for the audio cut in seconds, represented as a string. It must be
                      a numeric value greater than the start time.
Returns:
    str: A success message confirming the completion of the audio cutting operation, including
         the start and end time of the extracted segment and the path to the newly created audio file.
"""
```'''

    if not isinstance(audio_file, str) or not audio_file.strip():

        return "Error: 'audio_file' must be a non-empty string."

    try:

        start_time_val = float(start_time)

    except ValueError:

        return 'Error: Start time must be a numeric value.'

    if start_time_val < 0:

        return 'Error: Start time cannot be negative.'

    try:

        end_time_val = float(end_time)

    except ValueError:

        return 'Error: End time must be a numeric value.'

    if end_time_val < 0:

        return 'Error: End time cannot be negative.'

    if end_time_val <= start_time_val:

        return 'Error: End time must be greater than start time.'

    import os

    base_name = os.path.splitext(os.path.basename(audio_file))[0]

    output_path = f'./outputs/audio_processed/{base_name}_from_{start_time_val:.2f}s_to_{end_time_val:.2f}s.mp3'

    return (

        f'Audio cutting operation completed successfully. Extracted segment from '

        f'{start_time_val:.2f}s to {end_time_val:.2f}s. File created at: {output_path}'

    )
@mcp.tool()
@safe_tool
def AudioEditor_transcribe_audio_sync(audio_file: str) -> str:

    '''```python
    """
    Synchronously transcribe an audio file using AI-powered speech recognition.

    This function serves as a synchronous wrapper around the asynchronous transcription process,
    converting audio files to text using advanced speech recognition technology. It manages the
    async/await complexity internally and returns detailed transcription results, including the
    full text, timestamped segments, language detection, and processing statistics.

    Args:
        audio_file (str): The path to the audio file to be transcribed. Must be a non-empty string.

    Returns:
        tuple: A tuple containing four elements:
            - status (str): A status message indicating success with language and processing time,
              or error information if transcription failed.
            - full_text (str): The complete transcription as plain text, or an empty string on error.
            - segments_formatted (str): Formatted text showing timestamped segments with start/end
              times and confidence scores, or an empty string on error.
            - json_formatted (str): A pretty-formatted JSON string containing complete transcription
              data, including word-level timestamps and metadata, or an empty string on error.

    Notes:
        - Automatically detects the language in the audio file.
        - Provides word-level and segment-level timestamps for precise audio editing.
        - Returns confidence scores for quality assessment.
        - Handles various audio formats and sample rates automatically.
        - Processing time depends on audio length and complexity.
        - All timestamps are provided in seconds with decimal precision.
        - Function blocks until transcription is complete (synchronous).
        - For asynchronous usage, use process_transcription() directly instead.
    """
```'''

    mock_audio_db = {'url/to/audio.mp3': {'filename': 'demo_song.mp3', 'language': 'en', 'duration_sec': 185.4, 'full_text': "Walking down the midnight road, chasing dreams I've never known.\nEvery step a story told, in the rhythm of my own.", 'segments': [{'start': 0.0, 'end': 9.5, 'text': "Walking down the midnight road, chasing dreams I've never known.", 'confidence': 0.96, 'words': [{'word': 'Walking', 'start': 0.0, 'end': 0.6, 'confidence': 0.98}, {'word': 'down', 'start': 0.61, 'end': 0.85, 'confidence': 0.97}, {'word': 'the', 'start': 0.86, 'end': 0.95, 'confidence': 0.99}, {'word': 'midnight', 'start': 0.96, 'end': 1.32, 'confidence': 0.94}, {'word': 'road,', 'start': 1.33, 'end': 1.62, 'confidence': 0.95}, {'word': 'chasing', 'start': 1.63, 'end': 1.92, 'confidence': 0.93}, {'word': 'dreams', 'start': 1.93, 'end': 2.22, 'confidence': 0.92}, {'word': "I've", 'start': 2.23, 'end': 2.35, 'confidence': 0.97}, {'word': 'never', 'start': 2.36, 'end': 2.55, 'confidence': 0.96}, {'word': 'known.', 'start': 2.56, 'end': 2.84, 'confidence': 0.94}]}, {'start': 9.6, 'end': 18.3, 'text': 'Every step a story told, in the rhythm of my own.', 'confidence': 0.95, 'words': [{'word': 'Every', 'start': 9.6, 'end': 9.8, 'confidence': 0.96}, {'word': 'step', 'start': 9.81, 'end': 10.0, 'confidence': 0.95}, {'word': 'a', 'start': 10.01, 'end': 10.05, 'confidence': 0.99}, {'word': 'story', 'start': 10.06, 'end': 10.34, 'confidence': 0.94}, {'word': 'told,', 'start': 10.35, 'end': 10.6, 'confidence': 0.93}, {'word': 'in', 'start': 10.61, 'end': 10.7, 'confidence': 0.97}, {'word': 'the', 'start': 10.71, 'end': 10.8, 'confidence': 0.98}, {'word': 'rhythm', 'start': 10.81, 'end': 11.15, 'confidence': 0.92}, {'word': 'of', 'start': 11.16, 'end': 11.25, 'confidence': 0.98}, {'word': 'my', 'start': 11.26, 'end': 11.35, 'confidence': 0.96}, {'word': 'own.', 'start': 11.36, 'end': 11.58, 'confidence': 0.94}]}], 'processing_time_sec': 3.45}}

    if not isinstance(audio_file, str) or not audio_file.strip():

        return str(('Error: Invalid audio_file parameter. Must be a non-empty string.', '', '', ''))

    if audio_file not in mock_audio_db:

        return str((f"Error: Audio file '{audio_file}' not found in transcription database.", '', '', ''))

    data = mock_audio_db[audio_file]

    segments_formatted = ''

    for seg in data['segments']:

        segments_formatted += f"[{seg['start']:.2f}s - {seg['end']:.2f}s] (conf: {seg['confidence']:.2f}): {seg['text']}\n"

    import json

    json_formatted = json.dumps({'filename': data['filename'], 'language': data['language'], 'duration_sec': data['duration_sec'], 'full_text': data['full_text'], 'segments': data['segments'], 'processing_time_sec': data['processing_time_sec']}, indent=2)

    status = f"Success: Transcription completed in {data['processing_time_sec']:.2f}s (Language detected: {data['language']})"

    return str((status, data['full_text'], segments_formatted.strip(), json_formatted))
@mcp.tool()
@safe_tool
def analyze_sound(filepath: str) -> str:

    '''```python
    """
    Return basic properties for a given sound file key from a mock database.

    This tool simulates audio metadata lookup (duration, sample rate, channels, genre) using an in-memory
    example dataset. It validates the provided key and returns a formatted response if found.

    Args:
        filepath (str): Identifier or filename key to look up (e.g., "song1.mp3").

    Returns:
        str: A formatted block including duration, sample rate, channels, and genre. Returns an error message if
        the key is empty or not found in the mock database.
    """
    ```'''

    mock_sound_database = {

        "song1.mp3": {

            "duration": "3:45",

            "sample_rate": "44100 Hz",

            "channels": "2 (Stereo)",

            "genre": "Rock"

        },

        "song2.wav": {

            "duration": "5:12",

            "sample_rate": "48000 Hz",

            "channels": "2 (Stereo)",

            "genre": "Jazz"

        },

        "song3.aac": {

            "duration": "4:01",

            "sample_rate": "44100 Hz",

            "channels": "1 (Mono)",

            "genre": "Classical"

        }

    }

    if not filepath:

        return "Error: No filepath provided."

    if filepath not in mock_sound_database:

        return f"Error: File '{filepath}' not found in the database."

    sound_properties = mock_sound_database[filepath]

    output = (f"File: {filepath}\n"

              f"Duration: {sound_properties['duration']}\n"

              f"Sample Rate: {sound_properties['sample_rate']}\n"

              f"Channels: {sound_properties['channels']}\n"

              f"Genre: {sound_properties['genre']}")

    return output
@mcp.tool()
@safe_tool
def render_image(file_path: str) -> str:

    '''```python
    """
    Renders an image with additional visual information based on detection results.

    This function processes an image file specified by the `file_path` and overlays
    visual elements such as bounding boxes or highlighted regions to indicate detected
    objects. The rendering process enhances the image with 3D-style overlays or depth
    shading, depending on the detection results available for the input image.

    Args:
        file_path (str): The path to the image file to be rendered. Must be a non-empty
            string representing the location of the image file.

    Returns:
        str: A message indicating the success or failure of the rendering process.
            On success, it describes the rendered image and specifies the location
            where the output file is saved. On failure, it suggests running object
            detection first if no results are available.
    """
```'''

    mock_render_db = {'samples/detection_result_1.jpg': {'status': 'success', 'description': 'Rendered image with 3D-style bounding boxes for detected objects.', 'output_file': 'renders/detection_result_1_3d_overlay.png'}, 'samples/detection_result_2.jpg': {'status': 'success', 'description': 'Rendered image with highlighted regions for detected cars and pedestrians.', 'output_file': 'renders/detection_result_2_3d_overlay.png'}, 'samples/object_detection_test.png': {'status': 'success', 'description': 'Rendered image showing bounding boxes with depth shading for object detection test.', 'output_file': 'renders/object_detection_test_render.png'}}

    if not isinstance(file_path, str):

        raise TypeError('file_path must be a string representing the image file location.')

    if not file_path.strip():

        raise ValueError('file_path cannot be empty.')

    if file_path in mock_render_db:

        record = mock_render_db[file_path]

        return f"Image rendering completed: {record['description']} Saved to {record['output_file']}"

    else:

        return f"Rendering failed: No detection results found for '{file_path}'. Please run object detection first."
@mcp.tool()
@safe_tool
def create_design(design_request: str) -> str:

    '''```python
    """
    Initializes a quantum circuit design process and returns the file path for further processing.

    This function takes a design request string, validates it, and returns the path
    to the quantum_distribution design file without actually creating the file.
    The path is used for downstream tool processing.

    Args:
        design_request (str): A non-empty string representing the design request content.

    Returns:
        str: The path to the quantum_distribution design file that would be created.
    """
```'''

    if not isinstance(design_request, str) or not design_request.strip():

        raise ValueError('design_request must be a non-empty string representing the design request content.')

    request_str = design_request.strip()

    last_slash = max(request_str.rfind('/'), request_str.rfind('\\'))

    base_dir = request_str[:last_slash] if last_slash != -1 else '.'

    design_file_path = f"{base_dir}/quantum_design.json" if base_dir != '.' else "./quantum_design.json"

    return f"Quantum circuit design initialized. Design file would be saved to: {design_file_path}"
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

