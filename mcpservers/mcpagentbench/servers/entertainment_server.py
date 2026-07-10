"""
MCPAgentBench Entertainment MCP Server.
Concrete FastMCP server with 12 tools for the entertainment domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-entertainment")
@mcp.tool()
@safe_tool
def search_imdb(primary_title: str) -> str:

    '''"""
Search for movies and TV shows using their titles.
Args:
    primary_title (str): The exact title of the movie or TV show to search for.
Returns:
    str: A formatted string containing the title, genre, subtitle availability,
    and IMDb ID if a match is found. If no match is found, returns a message
    indicating that no results were found for the given title.
"""'''

    imdb_database = [{'title': 'Hotel Mumbai', 'genre': 'Suspense', 'subtitles': True, 'imdb_id': 'tt5461944'}, {'title': 'JT Leroy', 'genre': 'Non-fiction', 'subtitles': False, 'imdb_id': 'tt5460522'}, {'title': 'Captain Marvel', 'genre': 'Adventure', 'subtitles': True, 'imdb_id': 'tt4154664'}, {'title': 'Mad Max', 'genre': 'Fantasy', 'subtitles': True, 'imdb_id': 'tt1392190'}, {'title': 'Dogman', 'genre': 'Drama', 'subtitles': False, 'imdb_id': 'tt6768578'}, {'title': 'Say Anything', 'genre': 'Romance', 'subtitles': False, 'imdb_id': 'tt0098258'}, {'title': 'Alice in Wonderland', 'genre': 'Fantasy', 'subtitles': True, 'imdb_id': 'tt1014759'}, {'title': 'Hackers', 'genre': 'Drama', 'subtitles': True, 'imdb_id': 'tt0113243'}, {'title': 'Dr. Strangelove', 'genre': 'Comedy', 'subtitles': False, 'imdb_id': 'tt0057012'}, {'title': 'Hellboy', 'genre': 'Fantasy', 'subtitles': True, 'imdb_id': 'tt2274648'}, {'title': 'The Poseidon Adventure', 'genre': 'Adventure', 'subtitles': False, 'imdb_id': 'tt0069113'}]

    search_results = [entry for entry in imdb_database if entry['title'].lower() == primary_title.lower()]

    if not search_results:

        return f"No results found for the title '{primary_title}'. Please check the title and try again."

    result = search_results[0]

    response = f"Title: {result['title']}\nGenre: {result['genre']}\nSubtitles available: {('Yes' if result['subtitles'] else 'No')}\nIMDb ID: {result['imdb_id']}"

    return response
@mcp.tool()
@safe_tool
def get_directors(imdb_id: str) -> str:

    '''"""
Retrieve the directors of a movie.
Given a valid IMDb movie identifier, this function returns the name of the movie's director.
If the IMDb ID format is invalid or the movie cannot be found, an error message is returned.
Args:
    imdb_id (str): The IMDb identifier of the movie (e.g., 'tt0113243').
Returns:
    str: A message containing the director's name if found, or an error message if the IMDb ID
    is invalid or the movie is not found.
"""'''

    movie_directors_db = {'tt0098258': 'Cameron Crowe', 'tt0113243': 'Iain Softley', 'tt0057012': 'Stanley Kubrick', 'tt2274648': 'Neil Marshall', 'tt0167190': 'Sam Mendes'}

    if not isinstance(imdb_id, str) or not imdb_id.startswith('tt'):

        return 'Error: Invalid IMDb ID format. Please provide a valid IMDb ID.'

    director = movie_directors_db.get(imdb_id)

    if director:

        return f'The director of the movie with IMDb ID {imdb_id} is {director}.'

    else:

        return 'Error: Movie not found in the database. Please check the IMDb ID and try again.'
@mcp.tool()
@safe_tool
def itunes_search(artist: str) -> str:

    '''"""
Search the music library for tracks by a given artist name.
Args:
    artist (str): The exact name of the artist to search for.
Returns:
    str: A formatted string listing matching tracks in the format
        "Artist - Title (Album, Genre)" separated by newlines,
        or an error message if the input is invalid,
        or a message indicating no matches were found.
"""'''

    mock_itunes_library = [{'artist': 'El Alfa', 'title': 'La Romana', 'album': 'El Hombre', 'genre': 'Latin'}, {'artist': 'Frank Ocean', 'title': 'Nikes', 'album': 'Blonde', 'genre': 'R&B'}, {'artist': 'Karolina Protsenko', 'title': 'Closer', 'album': 'Fly', 'genre': 'Pop'}, {'artist': 'Brunettes Shoot Blondes', 'title': 'Every Monday', 'album': 'Bittersweet', 'genre': 'Rock'}, {'artist': 'Wolfgang Amadeus Mozart', 'title': 'Eine kleine Nachtmusik', 'album': 'Classical Favorites', 'genre': 'Classical'}]

    if not isinstance(artist, str) or not artist.strip():

        return 'Error: Invalid input. Please provide a valid search term.'

    artist = artist.strip().lower()

    results = []

    for track in mock_itunes_library:

        if artist == track['artist'].lower():

            results.append(track)

    if results:

        result_strings = [f"{track['artist']} - {track['title']} ({track['album']}, {track['genre']})" for track in results]

        return '\n'.join(result_strings)

    else:

        return 'No tracks found matching your search criteria.'
@mcp.tool()
@safe_tool
def itunes_play_song(song: str) -> str:

    '''"""
Play a specific song in iTunes using the song title.
Args:
    song (str): The exact title of the song to be played in iTunes.
Returns:
    str: A confirmation message indicating that the specified song is being played.
"""'''

    return f"Playing '{song}' on iTunes."
@mcp.tool()
@safe_tool
def recommend_musictracks(music_name: List[str], result_num: int) -> str:

    '''```python
"""
Generates music track recommendations based on provided seed identifiers, returning up to a specified number
of tracks per seed with complete metadata.
This function searches for tracks using seed identifiers and retrieves track metadata for each seed.
Music names should be provided exactly as specified with proper capitalization. The number
of tracks returned per seed is limited by the `result_num` parameter.
Args:
    music_name (List[str]): A list of seed identifiers to look up, such as album keys.
    result_num (int): The maximum number of tracks to return for each seed identifier.
Returns:
    str: A string representation of a list containing dictionaries of track metadata. Each dictionary includes
    details such as title, artist, album, genre, release date, and a preview URL.
Raises:
    ValueError: If `music_name` is not a list of strings or if `result_num` is not a positive integer.
"""
```'''

    mock_tracks_db = {'billboard_2023_album1_track1': {'title': 'Electric Horizon', 'artist': 'Neon Pulse', 'album': 'Skyline Dreams', 'genre': 'Synthpop', 'release_date': '2023-05-14', 'preview_url': 'https://mockstreaming.com/preview/electric_horizon'}, 'billboard_2023_album1_track3': {'title': 'Golden Rivers', 'artist': 'Aurora Fields', 'album': "Nature's Echo", 'genre': 'Folk Pop', 'release_date': '2023-07-22', 'preview_url': 'https://mockstreaming.com/preview/golden_rivers'}, 'deezer_similar_style_1': {'title': 'Skybound Love', 'artist': 'Crystal Waves', 'album': 'Blue Horizons', 'genre': 'Synthpop', 'release_date': '2022-11-02', 'preview_url': 'https://mockstreaming.com/preview/skybound_love'}, 'deezer_similar_style_2': {'title': 'Meadow Lullaby', 'artist': 'Willow Whisper', 'album': 'Evening Glow', 'genre': 'Folk Pop', 'release_date': '2022-09-15', 'preview_url': 'https://mockstreaming.com/preview/meadow_lullaby'}, 'jazz_inspired_1': {'title': 'Midnight Groove', 'artist': 'The Blue Tones', 'album': 'City Lights', 'genre': 'Jazz', 'release_date': '2021-04-09', 'preview_url': 'https://mockstreaming.com/preview/midnight_groove'}, 'jazz_inspired_2': {'title': 'Sax & The City', 'artist': 'Urban Quartet', 'album': 'Metropolitan Nights', 'genre': 'Jazz Fusion', 'release_date': '2020-08-21', 'preview_url': 'https://mockstreaming.com/preview/sax_and_the_city'}, 'upbeat_track_1': {'title': 'Dance Until Dawn', 'artist': 'Rhythm Rush', 'album': 'Night Fever', 'genre': 'Dance Pop', 'release_date': '2023-03-18', 'preview_url': 'https://mockstreaming.com/preview/dance_until_dawn'}, 'guts_vampire': {'title': 'vampire', 'artist': 'Olivia Rodrigo', 'album': 'GUTS', 'genre': 'Pop Rock', 'release_date': '2023-06-30', 'preview_url': 'https://mockstreaming.com/preview/olivia_rodrigo_vampire'}, 'guts_bad_idea_right': {'title': 'bad idea right?', 'artist': 'Olivia Rodrigo', 'album': 'GUTS', 'genre': 'Pop Punk', 'release_date': '2023-08-11', 'preview_url': 'https://mockstreaming.com/preview/olivia_rodrigo_bad_idea_right'}, 'guts_get_him_back': {'title': 'get him back!', 'artist': 'Olivia Rodrigo', 'album': 'GUTS', 'genre': 'Pop Rock', 'release_date': '2023-09-08', 'preview_url': 'https://mockstreaming.com/preview/olivia_rodrigo_get_him_back'}, 'guts_ballad_of_a_homeschooled_girl': {'title': 'ballad of a homeschooled girl', 'artist': 'Olivia Rodrigo', 'album': 'GUTS', 'genre': 'Pop Punk', 'release_date': '2023-09-08', 'preview_url': 'https://mockstreaming.com/preview/olivia_rodrigo_ballad_of_a_homeschooled_girl'}, 'guts_logical': {'title': 'logical', 'artist': 'Olivia Rodrigo', 'album': 'GUTS', 'genre': 'Pop', 'release_date': '2023-09-08', 'preview_url': 'https://mockstreaming.com/preview/olivia_rodrigo_logical'}, 'guts_lacy': {'title': 'lacy', 'artist': 'Olivia Rodrigo', 'album': 'GUTS', 'genre': 'Indie Pop', 'release_date': '2023-09-08', 'preview_url': 'https://mockstreaming.com/preview/olivia_rodrigo_lacy'}}

    mock_music_db = {'guts': ['guts_vampire', 'guts_bad_idea_right', 'guts_get_him_back', 'guts_ballad_of_a_homeschooled_girl', 'guts_logical', 'guts_lacy'], 'jazz_inspired': ['jazz_inspired_1', 'jazz_inspired_2'], 'deezer_similar': ['deezer_similar_style_1', 'deezer_similar_style_2'], 'billboard_2023_album1': ['billboard_2023_album1_track1', 'billboard_2023_album1_track3']}

    if not isinstance(music_name, list) or not all((isinstance(tid, str) for tid in music_name)):

        return "Error: 'music_name' must be a list of strings representing track IDs."

    if not isinstance(result_num, int) or result_num <= 0:

        return "Error: 'result_num' must be a positive integer."

    recommendations = []

    seen_track_ids = set()

    for seed in music_name:

        track_ids = mock_music_db.get(seed.lower()) if isinstance(seed, str) else None

        if not track_ids:

            continue

        for track_id in track_ids[:result_num]:

            if track_id in seen_track_ids:

                continue

            seen_track_ids.add(track_id)

            track_meta = mock_tracks_db.get(track_id)

            if track_meta:

                recommendations.append(track_meta)

    if not recommendations:

        return 'No recommendations found for the given track IDs and filter criteria.'

    return str(recommendations)
@mcp.tool()
@safe_tool
def get_players(target_players: List[str]) -> str:

    '''```python
    """
    Retrieves detailed information about specified players from a sports team.

    This function accepts a list of player names and returns a formatted string
    containing comprehensive details about each player, including their team
    affiliations, positions, contact information, career achievements, and fun
    facts.

    Args:
        target_players (List[str]): A list of player names for which information
            is to be retrieved. Each name should be a string.

    Returns:
        str: A formatted string with detailed information about the requested
        players. If no matching players are found, an error message is returned.
    """
```'''

    mock_player_db = {'LeBron James': {'team': 'Los Angeles Lakers', 'position': 'Forward', 'contact': 'lebron.james@nba.com', 'career_achievements': ['4× NBA champion', '4× NBA Most Valuable Player', 'NBA All-Star 19 times'], 'fun_fact': 'LeBron James is the youngest player to score 30,000 career points in NBA history.'}, 'Stephen Curry': {'team': 'Golden State Warriors', 'position': 'Guard', 'contact': 'stephen.curry@nba.com', 'career_achievements': ['4× NBA champion', '2× NBA Most Valuable Player', 'NBA all-time leader in three-pointers made'], 'fun_fact': 'Stephen Curry is credited with revolutionizing the game with his exceptional three-point shooting.'}, 'Anthony Davis': {'team': 'Los Angeles Lakers', 'position': 'Forward-Center', 'contact': 'anthony.davis@nba.com', 'career_achievements': ['NBA champion (2020)', '8× NBA All-Star', '4× NBA All-Defensive First Team', 'NBA All-Star Game MVP (2017)'], 'fun_fact': "Anthony Davis is known for his exceptional defensive skills and was nicknamed 'The Brow' due to his distinctive unibrow."}, 'Donte DiVincenzo': {'team': 'Golden State Warriors', 'position': 'Guard', 'contact': 'donte.divincenzo@nba.com', 'career_achievements': ['NBA champion (2021)', 'NCAA champion (2018)', 'NCAA Final Four Most Outstanding Player (2018)'], 'fun_fact': "Donte DiVincenzo was a key player in Villanova's 2018 NCAA championship run and is known for his clutch performances."}}

    if not isinstance(target_players, list) or not all((isinstance(p, str) for p in target_players)):

        return "Error: 'target_players' must be a list of player names (strings)."

    available_players = {name: mock_player_db[name] for name in target_players if name in mock_player_db}

    if not available_players:

        return 'Error: No matching players found in the database for the given target_players list.'

    result_lines = []

    for (name, info) in available_players.items():

        result_lines.append(f"Player: {name}\nTeam: {info['team']}\nPosition: {info['position']}\nContact: {info['contact']}\nCareer Achievements: {', '.join(info['career_achievements'])}\nFun Fact: {info['fun_fact']}\n")

    return '\n'.join(result_lines)
@mcp.tool()
@safe_tool
def get_teams(nameFilter: str) -> str:

    '''```python
    """
    Retrieves a list of teams and their members for specified sports leagues.

    This function returns detailed information about teams and their members
    for various sports leagues, including NBA, NFL, MLB, NHL, CBB, CFC, and NCAA.
    The information includes team names and member details such as name and position.

    Args:
        nameFilter (str): The name of the league to filter teams by. Must be one of
            'NBA', 'NFL', 'MLB', 'NHL', 'CBB', 'CFC', or 'NCAA'.

    Returns:
        str: A formatted string containing the list of teams and their members for
        the specified league. If the league name is invalid or the input type is incorrect,
        an error message is returned.
    """
```'''

    mock_teams_db = {'NBA': [{'team_name': 'Los Angeles Lakers', 'members': [{'name': 'LeBron James', 'position': 'Forward'}, {'name': 'Anthony Davis', 'position': 'Forward-Center'}, {'name': "D'Angelo Russell", 'position': 'Guard'}, {'name': 'Russell Westbrook', 'position': 'Guard'}, {'name': 'Thomas Bryant', 'position': 'Center'}, {'name': 'Troy Brown Jr.', 'position': 'Forward'}, {'name': 'Austin Reaves', 'position': 'Guard'}, {'name': 'Lonnie Walker IV', 'position': 'Guard'}, {'name': 'Patrick Beverley', 'position': 'Guard'}, {'name': 'Wenyen Gabriel', 'position': 'Forward'}]}, {'team_name': 'Golden State Warriors', 'members': [{'name': 'Stephen Curry', 'position': 'Guard'}, {'name': 'Klay Thompson', 'position': 'Guard'}, {'name': 'Draymond Green', 'position': 'Forward'}, {'name': 'Jordan Poole', 'position': 'Guard'}, {'name': 'Kevon Looney', 'position': 'Center'}, {'name': 'Andrew Wiggins', 'position': 'Forward'}, {'name': 'Moses Moody', 'position': 'Guard'}, {'name': 'Jonathan Kuminga', 'position': 'Forward'}, {'name': 'JaMychal Green', 'position': 'Forward'}, {'name': 'Donte DiVincenzo', 'position': 'Guard'}]}], 'NFL': [{'team_name': 'New England Patriots', 'members': [{'name': 'Mac Jones', 'position': 'Quarterback'}, {'name': 'Matthew Judon', 'position': 'Linebacker'}, {'name': 'Jakobi Meyers', 'position': 'Wide Receiver'}]}, {'team_name': 'Dallas Cowboys', 'members': [{'name': 'Dak Prescott', 'position': 'Quarterback'}, {'name': 'Micah Parsons', 'position': 'Linebacker'}, {'name': 'CeeDee Lamb', 'position': 'Wide Receiver'}]}], 'MLB': [{'team_name': 'New York Yankees', 'members': [{'name': 'Aaron Judge', 'position': 'Outfielder'}, {'name': 'Gerrit Cole', 'position': 'Pitcher'}, {'name': 'Giancarlo Stanton', 'position': 'Outfielder'}]}], 'NHL': [{'team_name': 'Chicago Blackhawks', 'members': [{'name': 'Jonathan Toews', 'position': 'Center'}, {'name': 'Patrick Kane', 'position': 'Right Wing'}, {'name': 'Seth Jones', 'position': 'Defenseman'}]}], 'CBB': [{'team_name': 'Duke Blue Devils', 'members': [{'name': 'Jeremy Roach', 'position': 'Guard'}, {'name': 'Kyle Filipowski', 'position': 'Forward'}, {'name': 'Tyrese Proctor', 'position': 'Guard'}]}], 'CFC': [{'team_name': 'Clemson Tigers Football', 'members': [{'name': 'Cade Klubnik', 'position': 'Quarterback'}, {'name': 'Will Shipley', 'position': 'Running Back'}, {'name': 'Barrett Carter', 'position': 'Linebacker'}]}], 'NCAA': [{'team_name': 'Alabama Crimson Tide', 'members': [{'name': 'Bryce Young', 'position': 'Quarterback'}, {'name': 'Will Anderson Jr.', 'position': 'Linebacker'}, {'name': 'Brian Robinson Jr.', 'position': 'Running Back'}]}]}

    if not isinstance(nameFilter, str):

        return 'Error: nameFilter must be a string.'

    nameFilter_upper = nameFilter.strip().upper()

    if nameFilter_upper not in mock_teams_db:

        valid_keys = ', '.join(mock_teams_db.keys())

        return f"Error: Invalid league filter '{nameFilter}'. Valid options are: {valid_keys}."

    teams_list = mock_teams_db[nameFilter_upper]

    output_lines = [f'Teams in {nameFilter_upper}:']

    for team in teams_list:

        output_lines.append(f"- {team['team_name']}")

        for member in team['members']:

            output_lines.append(f"   • {member['name']} ({member['position']})")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_book_details_by_id(id: List[int]) -> str:

    '''```python
"""
Get book details by ID.
This function retrieves details of books based on their unique identifiers (IDs).
It accepts a list of integer IDs and returns a formatted string containing the
details of each book, including title, authors, publisher, year, edition, and ID.
If an ID does not correspond to any book, a message indicating no details found
is included for that ID.
Args:
    id (List[int]): A list of integers representing the unique identifiers of the books.
Returns:
    str: A formatted string with the details of the books corresponding to the provided IDs.
         If an ID is not found, the string will include a message indicating no details found
         for that particular ID.
"""
```'''

    mock_book_db = {1: {'title': 'The C Programming Language', 'authors': ['Brian W. Kernighan', 'Dennis M. Ritchie'], 'publisher': 'Prentice Hall', 'year': 1988, 'edition': '2nd', 'id': 1}, 2: {'title': 'Introduction to Algorithms', 'authors': ['Thomas H. Cormen', 'Charles E. Leiserson', 'Ronald L. Rivest', 'Clifford Stein'], 'publisher': 'MIT Press', 'year': 2009, 'edition': '3rd', 'id': 2}, 3: {'title': 'Design Patterns: Elements of Reusable Object-Oriented Software', 'authors': ['Erich Gamma', 'Richard Helm', 'Ralph Johnson', 'John Vlissides'], 'publisher': 'Addison-Wesley', 'year': 1994, 'edition': '1st', 'id': 3}, 4: {'title': 'Fluent Python', 'authors': ['Luciano Ramalho'], 'publisher': "O'Reilly Media", 'year': 2015, 'edition': '1st', 'id': 4}, 5: {'title': 'Head First Design Patterns', 'authors': ['Eric Freeman', 'Bert Bates', 'Kathy Sierra', 'Elisabeth Robson'], 'publisher': "O'Reilly Media", 'year': 2004, 'edition': '1st', 'id': 5}}

    if not isinstance(id, list) or not all((isinstance(i, int) for i in id)):

        return "Error: 'id' parameter must be a list of integers."

    if not id:

        return 'Error: No ID numbers provided.'

    results = []

    for code in id:

        if code in mock_book_db:

            book = mock_book_db[code]

            results.append(f"Title: {book['title']}\nAuthors: {', '.join(book['authors'])}\nPublisher: {book['publisher']}\nYear: {book['year']}\nEdition: {book['edition']}\nID: {book['id']}\n")

        else:

            results.append(f'ID: {code} - No details found in database.')

    return '\n'.join(results)
@mcp.tool()
@safe_tool
def diceRoll(sides: int, count: int, modifier: int, roll_type: str) -> str:

    '''```python
    """
    Roll D&D dice with customizable options.

    This function simulates rolling dice commonly used in Dungeons & Dragons
    games, allowing for various roll types and modifiers. It supports different
    contexts such as attack rolls, saving throws, skill checks, and more.

    Args:
        sides (int): The number of sides on each die. Must be greater than 1.
        count (int): The number of dice to roll. Must be a positive integer.
        modifier (int): A numerical modifier to be added to the total roll.
        roll_type (str): The type of roll being performed, such as 'attack',
            'saving throw', or 'skill check'. Must be a non-empty string.

    Returns:
        str: A formatted string describing the roll context, individual dice
        results, the modifier applied, and the total result.
    """
```'''

    import random

    mock_roll_contexts = {'attack': {'default_sides': 20, 'description': 'You swing your weapon in an attack roll.'}, 'saving throw': {'default_sides': 20, 'description': 'You attempt to resist a harmful effect with a saving throw.'}, 'skill check': {'default_sides': 20, 'description': 'You test your skills in a tense moment.'}, 'trap disarm': {'default_sides': 20, 'description': 'You attempt to disarm a hidden trap.'}, 'puzzle solve': {'default_sides': 20, 'description': 'You try to solve the puzzle under time pressure.'}, 'boss battle': {'default_sides': 20, 'description': 'You face the boss in a climactic roll.'}}

    if not isinstance(count, int) or count <= 0:

        return "Error: 'count' must be a positive integer."

    if not isinstance(modifier, int):

        return "Error: 'modifier' must be an integer."

    if not isinstance(roll_type, str) or roll_type.strip() == '':

        return "Error: 'roll_type' must be a non-empty string."

    if sides is not None and (not isinstance(sides, int) or sides <= 1):

        return "Error: 'sides' must be an integer greater than 1."

    context = mock_roll_contexts.get(roll_type.lower())

    dice_sides = sides

    if dice_sides is None:

        dice_sides = context['default_sides'] if context else 20

    rolls = [random.randint(1, dice_sides) for _ in range(count)]

    total = sum(rolls) + modifier

    description = context['description'] if context else f'You roll {count}d{dice_sides}.'

    result_str = f'{description}\nRolls: {rolls} (d{dice_sides})\nModifier: {modifier:+}\nTotal: {total}'

    return result_str
@mcp.tool()
@safe_tool
def dmagent_ask_narrative(question: str, theme_hint: str, tone: str, focus_element: str) -> str:

    '''```python
    """
    Provides an interactive assistant for Dungeon Masters in Dungeons & Dragons 5e,
    focusing on narrative development. This tool poses targeted questions to help
    shape the adventure's theme, setting, and mood, aiding in defining story elements
    such as environment, villain style, puzzle flavor, traps, and rewards. The responses
    assist the DM in crafting immersive read-aloud text, narrative hooks, and maintaining
    thematic consistency. This function emphasizes worldbuilding and storytelling,
    complementing other tools that handle rules or dice mechanics.

    Args:
        question (str): The initial narrative question posed by the DM.
        theme_hint (str): An optional hint to guide the thematic direction of the narrative.
        tone (str): An optional descriptor to set the tone of the adventure, such as
            'serious' or 'lighthearted'.
        focus_element (str): An optional focus area for the narrative, such as 'boss design'
            or 'trap'.

    Returns:
        str: A follow-up narrative question tailored to the provided inputs, aiding in
        the development of the adventure's theme and story elements.
    """
```'''

    mock_db = {'default': ['What overall theme should the one-shot have—dark horror, epic fantasy, or whimsical adventure?', 'What sort of environment will the party begin in—forest, dungeon, city, or something else?', "Describe the villain's personality—cunning mastermind, brute force, tragic figure?"], 'undead horror': {'serious': {'boss design': ['Should the undead boss be a cunning necromancer or a mindless horde leader?', "What cursed artifact fuels the villain's dark magic?"], 'trap': ['Should the traps be bone-crushing mechanical devices or necrotic wards that drain life?', 'What eerie signs warn of the traps ahead?'], 'puzzle': ["What kind of riddle could be carved into the crypt walls to seal the villain's chamber?", 'Should the puzzle require interpreting ancient runes or aligning skeletal remains?'], 'reward': ['What holy relic could banish undead from the realm as a final reward?', 'Should the reward be a weapon, armor, or magical trinket imbued with radiant energy?']}}, 'jungle exploration': {'lighthearted': {'boss design': ['Should the jungle boss be a mischievous trickster spirit or a territorial beast?', "What unusual weakness does the boss have tied to the jungle's flora?"]}}, 'arcane mystery': {'gritty': {'puzzle': ['Should the puzzle involve rearranging arcane sigils or deciphering a forbidden incantation?', 'What is at stake if the puzzle is solved incorrectly?']}}}

    if not isinstance(question, str) or not question.strip():

        raise ValueError("Parameter 'question' must be a non-empty string.")

    if theme_hint is not None and (not isinstance(theme_hint, str)):

        raise ValueError("Parameter 'theme_hint' must be a string if provided.")

    if tone is not None and (not isinstance(tone, str)):

        raise ValueError("Parameter 'tone' must be a string if provided.")

    if focus_element is not None and (not isinstance(focus_element, str)):

        raise ValueError("Parameter 'focus_element' must be a string if provided.")

    theme_key = theme_hint.strip().lower() if theme_hint else None

    tone_key = tone.strip().lower() if tone else None

    focus_key = focus_element.strip().lower() if focus_element else None

    matched_prompts = None

    if theme_key and theme_key in mock_db:

        theme_data = mock_db[theme_key]

        if isinstance(theme_data, dict) and tone_key and (tone_key in theme_data):

            tone_data = theme_data[tone_key]

            if focus_key and focus_key in tone_data:

                matched_prompts = tone_data[focus_key]

        elif isinstance(theme_data, list):

            matched_prompts = theme_data

    if not matched_prompts:

        matched_prompts = mock_db['default']

    import random

    follow_up_question = random.choice(matched_prompts)

    return f'Narrative question based on your input: {follow_up_question}\n(Original question: {question})'
@mcp.tool()
@safe_tool
def dmagent_ask_rule(question: str, rule_category: str, complexity_level: str, edition: str) -> str:

    '''```python
"""
An interactive Dungeon Master assistant for Dungeons & Dragons rules. This function helps clarify mechanical or rules-related questions to ensure encounters, abilities, traps, puzzles, or combat are resolved correctly. It aims to ensure that generated adventures adhere to system mechanics, including stat blocks, challenge ratings, saving throw mechanics, and item properties. The focus is on mechanics and system compliance, complementing narrative aspects handled by other tools.
Args:
    question (str): The specific rules-related question to be addressed.
    rule_category (str): The category of rules to query, such as 'combat', 'traps', 'items', 'monsters', or 'spellcasting'.
    complexity_level (str): The complexity level of the rules, which can be 'basic', 'standard', or 'advanced'.
    edition (str): The edition of the game rules to use, such as '5e', '3.5e', or 'Pathfinder'.
Returns:
    str: A formatted string containing the edition, rule category, complexity level, and guidance for the given question.
"""
```'''

    mock_rules_db = {'combat': {'basic': 'In D&D 5e, combat is turn-based. Each creature gets movement, one action, and possibly a bonus action.', 'standard': 'For a CR 5 boss, typical AC ranges from 15-17, HP around 150, and attack bonus +6 to +8. CR 10 bosses often have legendary actions, while CR 15 bosses may have lair actions.', 'advanced': 'CR calculation considers HP, AC, damage per round, save DCs, resistances, and immunities according to DMG p. 274-281.'}, 'traps': {'basic': 'Traps usually require a Perception check to detect and a Dexterity saving throw to avoid damage.', 'standard': 'A medium-difficulty trap may have a DC 15 Perception check to detect and DC 15 Dexterity save to avoid 4d10 damage.', 'advanced': "Complex traps may involve multiple mechanisms, requiring multiple ability checks or saving throws over several rounds. Consult Xanathar's Guide for examples."}, 'items': {'basic': 'Magic items are ranked: common, uncommon, rare, very rare, legendary.', 'standard': 'An uncommon item might give +1 AC or +1 to attack rolls; a rare item could grant resistance to a damage type or 1/day spell use.', 'advanced': 'Determine rarity by comparing bonuses, charges, and game-breaking potential. See DMG p. 285 for guidelines.'}, 'monsters': {'basic': 'Monsters have stat blocks including HP, AC, attacks, and abilities.', 'standard': 'A CR 5 monster is a serious threat to a party of level 5 characters, while CR 10 is deadly for level 10 parties.', 'advanced': 'Adjust monster CR based on environment, lair actions, legendary actions, and party composition.'}, 'spellcasting': {'basic': 'Spellcasters have spell slots per level and known/prepared spells.', 'standard': 'Saving throws vs. spells use DC = 8 + proficiency bonus + spellcasting ability modifier.', 'advanced': 'Consider concentration rules, counterspells, spell components, and upcasting effects.'}}

    supported_editions = ['5e', '3.5e', 'Pathfinder']

    if edition and edition not in supported_editions:

        return f"Error: Unsupported edition '{edition}'. Supported editions: {', '.join(supported_editions)}."

    selected_edition = edition if edition else '5e'

    selected_category = (rule_category or 'combat').lower()

    selected_complexity = (complexity_level or 'standard').lower()

    if selected_category not in mock_rules_db:

        return f"Error: Unknown rule category '{selected_category}'. Available categories: {', '.join(mock_rules_db.keys())}."

    if selected_complexity not in mock_rules_db[selected_category]:

        return f"Error: Unknown complexity level '{selected_complexity}'. Available levels: {', '.join(mock_rules_db[selected_category].keys())}."

    base_guidance = mock_rules_db[selected_category][selected_complexity]

    if question:

        q_lower = question.lower()

        if 'cr' in q_lower:

            answer = 'For balance, a boss CR should match the average party level +2 for a challenging fight.'

        elif 'saving throw' in q_lower:

            answer = 'Dexterity saves are common for traps; Constitution or Wisdom saves may apply for magical effects.'

        elif 'magical reward' in q_lower or 'item' in q_lower:

            answer = "Theme-appropriate reward: For a desert adventure, a 'Ring of Sandstride' (uncommon) allows movement through sand without penalty."

        else:

            answer = "The rule depends on context; refer to the Dungeon Master's Guide for detailed guidance."

        return f'[Edition: {selected_edition.upper()} | Category: {selected_category} | Complexity: {selected_complexity}]\nBase Guidance: {base_guidance}\nQ: {question}\nA: {answer}'

    else:

        return f'[Edition: {selected_edition.upper()} | Category: {selected_category} | Complexity: {selected_complexity}]\nGuidance: {base_guidance}'
@mcp.tool()
@safe_tool
def strategy_guide(situation: str) -> str:

    '''```python
    """
    Generates a strategic analysis based on the provided situation.

    This function analyzes the given situation and returns a detailed strategic
    analysis. The analysis includes recommendations on environment utilization,
    player flow, resource distribution, gameplay balance, engagement strategy,
    and technical optimization, among other factors.

    Args:
        situation (str): A description of the current situation requiring
            strategic analysis. Must be a non-empty string.

    Returns:
        str: A strategic analysis tailored to the specified situation, outlining
        key objectives, constraints, and actionable strategies.
    """
```'''

    mock_strategic_analyses = {'battle royal game in Unreal Engine 5': "Strategic Analysis:\n- Environment Utilization: Design varied terrain features (urban ruins, forests, open plains) to encourage diverse combat tactics.\n- Player Flow: Implement shrinking safe zones that force player encounters while allowing strategic positioning.\n- Resource Distribution: Place high-value loot in riskier zones to incentivize movement and risk-taking.\n- Gameplay Balance: Ensure weapon variety and counter-play mechanics to support different playstyles.\n- Engagement Strategy: Integrate environmental hazards (e.g., storms, collapsing buildings) to keep gameplay dynamic.\n- Technical Optimization: Utilize Unreal Engine 5's Nanite and Lumen for realistic visuals without sacrificing performance.", '3D environment battle scene': 'Strategic Analysis:\n- Terrain Design: Incorporate verticality, cover points, and destructible elements to enhance tactical depth.\n- Chokepoints and Open Areas: Balance narrow corridors for ambushes with wide-open zones for long-range engagements.\n- Lighting Strategy: Use dynamic lighting to create tension and reveal or conceal movement.\n- Spawn Logic: Position player and item spawns to prevent unfair advantages.\n- Replayability: Modular asset design to allow multiple layout variations.'}

    if not isinstance(situation, str) or not situation.strip():

        raise ValueError("Parameter 'situation' must be a non-empty string.")

    key = situation.strip().lower()

    for (scenario_key, analysis) in mock_strategic_analyses.items():

        if key in scenario_key.lower():

            return analysis

    return f"Strategic Analysis for '{situation}':\n- Identify key objectives and constraints in the current situation.\n- Assess strengths, weaknesses, opportunities, and threats (SWOT analysis).\n- Determine resource allocation and risk mitigation measures.\n- Develop phased action plans with clear milestones.\n- Monitor progress and adapt strategy based on evolving conditions."
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

