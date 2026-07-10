"""
BFCL Social MCP Server.
Wraps TwitterAPI as MCP tools for the BFCL benchmark.
"""
import json
from typing import List
from mcp.server.fastmcp import FastMCP
from agenttim.bfcl.func_source_code.posting_api import TwitterAPI
from agenttim.mcpservers.mcpbfcl.servers._error_handler import safe_tool
mcp = FastMCP("mcpbfcl-social")
_instance = TwitterAPI()
@mcp.tool()
def admin_load_scenario(config_json: str, long_context: bool = False) -> str:

    """Load a scenario configuration into the TwitterAPI instance.

    Args:
        config_json (str): JSON string with the scenario configuration.
        long_context (bool): If True, extend state with long-context data.

    Returns:
        str: "OK" on success.
    """

    _instance._load_scenario(json.loads(config_json), long_context=long_context)

    return "OK"
@mcp.tool()
def admin_get_state() -> str:

    """Return the current public state of the TwitterAPI as JSON.

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
def authenticate_twitter(username: str, password: str) -> str:

    """Authenticate a user with username and password.

    Args:
        username (str): Username of the user.
        password (str): Password of the user.

    Returns:
        authentication_status (bool): True if authenticated, False otherwise.
    """

    return json.dumps(

        _instance.authenticate_twitter(username=username, password=password),

        default=str,

    )
@mcp.tool()
@safe_tool
def posting_get_login_status() -> str:

    """Get the login status of the current user.

    Returns:
        login_status (bool): True if the current user is logged in, False otherwise.
    """

    return json.dumps(_instance.posting_get_login_status(), default=str)
@mcp.tool()
@safe_tool
def post_tweet(

    content: str, tags: List[str] = [], mentions: List[str] = []
) -> str:

    """Post a tweet for the authenticated user.

    Args:
        content (str): Content of the tweet.
        tags (List[str]): [Optional] List of tags for the tweet. Tag name should start with #. This is only relevant if the user wants to add tags to the tweet.
        mentions (List[str]): [Optional] List of users mentioned in the tweet. Mention name should start with @. This is only relevant if the user wants to add mentions to the tweet.

    Returns:
        id (int): ID of the posted tweet.
        username (str): Username of the poster.
        content (str): Content of the tweet.
        tags (List[str]): List of tags associated with the tweet.
        mentions (List[str]): List of users mentioned in the tweet.
    """

    return json.dumps(

        _instance.post_tweet(content=content, tags=tags, mentions=mentions),

        default=str,

    )
@mcp.tool()
@safe_tool
def retweet(tweet_id: int) -> str:

    """Retweet a tweet for the authenticated user.

    Args:
        tweet_id (int): ID of the tweet to retweet.

    Returns:
        retweet_status (str): Status of the retweet action.
    """

    return json.dumps(_instance.retweet(tweet_id=tweet_id), default=str)
@mcp.tool()
@safe_tool
def comment(tweet_id: int, comment_content: str) -> str:

    """Comment on a tweet for the authenticated user.

    Args:
        tweet_id (int): ID of the tweet to comment on.
        comment_content (str): Content of the comment.

    Returns:
        comment_status (str): Status of the comment action.
    """

    return json.dumps(

        _instance.comment(tweet_id=tweet_id, comment_content=comment_content),

        default=str,

    )
@mcp.tool()
@safe_tool
def mention(tweet_id: int, mentioned_usernames: List[str]) -> str:

    """Mention specified users in a tweet.

    Args:
        tweet_id (int): ID of the tweet where users are mentioned.
        mentioned_usernames (List[str]): List of usernames to be mentioned.

    Returns:
        mention_status (str): Status of the mention action.
    """

    return json.dumps(

        _instance.mention(

            tweet_id=tweet_id, mentioned_usernames=mentioned_usernames

        ),

        default=str,

    )
@mcp.tool()
@safe_tool
def follow_user(username_to_follow: str) -> str:

    """Follow a user for the authenticated user.

    Args:
        username_to_follow (str): Username of the user to follow.

    Returns:
        follow_status (bool): True if followed, False if already following.
    """

    return json.dumps(

        _instance.follow_user(username_to_follow=username_to_follow), default=str

    )
@mcp.tool()
@safe_tool
def list_all_following() -> str:

    """List all users that the authenticated user is following.

    Returns:
        following_list (List[str]): List of all users that the authenticated user is following.
    """

    return json.dumps(_instance.list_all_following(), default=str)
@mcp.tool()
@safe_tool
def unfollow_user(username_to_unfollow: str) -> str:

    """Unfollow a user for the authenticated user.

    Args:
        username_to_unfollow (str): Username of the user to unfollow.

    Returns:
        unfollow_status (bool): True if unfollowed, False if not following.
    """

    return json.dumps(

        _instance.unfollow_user(username_to_unfollow=username_to_unfollow),

        default=str,

    )
@mcp.tool()
@safe_tool
def get_tweet(tweet_id: int) -> str:

    """Retrieve a specific tweet.

    Args:
        tweet_id (int): ID of the tweet to retrieve.

    Returns:
        id (int): ID of the retrieved tweet.
        username (str): Username of the tweet's author.
        content (str): Content of the tweet.
        tags (List[str]): List of tags associated with the tweet.
        mentions (List[str]): List of users mentioned in the tweet.
    """

    return json.dumps(_instance.get_tweet(tweet_id=tweet_id), default=str)
@mcp.tool()
@safe_tool
def get_user_tweets(username: str) -> str:

    """Retrieve all tweets from a specific user.

    Args:
        username (str): Username of the user whose tweets to retrieve.

    Returns:
        user_tweets (List[Dict]): List of dictionaries, each containing tweet information.
            - id (int): ID of the retrieved tweet.
            - username (str): Username of the tweet's author.
            - content (str): Content of the tweet.
            - tags (List[str]): List of tags associated with the tweet.
            - mentions (List[str]): List of users mentioned in the tweet.
    """

    return json.dumps(_instance.get_user_tweets(username=username), default=str)
@mcp.tool()
@safe_tool
def search_tweets(keyword: str) -> str:

    """Search for tweets containing a specific keyword.

    Args:
        keyword (str): Keyword to search for in the content of the tweets.

    Returns:
        matching_tweets (List[Dict]): List of dictionaries, each containing tweet information.
            - id (int): ID of the retrieved tweet.
            - username (str): Username of the tweet's author.
            - content (str): Content of the tweet.
            - tags (List[str]): List of tags associated with the tweet.
            - mentions (List[str]): List of users mentioned in the tweet.
    """

    return json.dumps(_instance.search_tweets(keyword=keyword), default=str)
@mcp.tool()
@safe_tool
def get_tweet_comments(tweet_id: int) -> str:

    """Retrieve all comments for a specific tweet.

    Args:
        tweet_id (int): ID of the tweet to retrieve comments for.

    Returns:
        comments (List[Dict]): List of dictionaries, each containing comment information.
            - username (str): Username of the commenter.
            - content (str): Content of the comment.
    """

    return json.dumps(

        _instance.get_tweet_comments(tweet_id=tweet_id), default=str

    )
@mcp.tool()
@safe_tool
def get_user_stats(username: str) -> str:

    """Get statistics for a specific user.

    Args:
        username (str): Username of the user to get statistics for.

    Returns:
        tweet_count (int): Number of tweets posted by the user.
        following_count (int): Number of users the specified user is following.
        retweet_count (int): Number of retweets made by the user.
    """

    return json.dumps(_instance.get_user_stats(username=username), default=str)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

