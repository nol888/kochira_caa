"""
Twitter timeline follower.

Broadcasts a Twitter user's timeline into IRC. Provides tweeting capabilities as well as
Markov-chain text generation with a compatible Brain.
"""

import time
import twitter

from threading import Thread
from twitter import Twitter, TwitterStream, TwitterHTTPError
from kochira import config
from kochira.service import Service, Config
from kochira.auth import requires_permission

service = Service(__name__, __doc__)

TWEET_ID_REGEX = r"(?:https?://(?:m\.|www\.)?twitter.com/[^/]+/status/)?(?P<id>[0-9]+)"

@service.config
class Config(Config):
    class OAuth(config.Config):
        consumer_key = config.Field(doc="Twitter API consumer key.")
        consumer_secret = config.Field(doc="Twitter API consumer secret.")
        token = config.Field(doc="Twitter API OAuth token.")
        token_secret = config.Field(doc="Twitter API OAuth token secret.")

    oauth = config.Field(doc="OAuth parameters.",
                         type=OAuth)

@service.setup
def make_twitter(ctx):
    ctx.storage.api = Twitter(auth=twitter.OAuth(**ctx.config.oauth._fields))

@service.command(r"tweet (?P<message>.+)$", mention=True)
@service.command(r"!tweet (?P<message>.+)$")
@requires_permission("tweet")
def tweet(ctx, message):
    """
    Tweet

    Tweet the given text.
    """
    try:
        tweet = ctx.storage.api.statuses.update(status=truncate(message))
        ctx.message("https://twitter.com/{0[user][screen_name]}/status/{0[id_str]}".format(tweet))
    except TwitterHTTPError as e:
        for error in e.response_data['errors']:
            ctx.respond("Twitter returned error: {}".format(error['message']))

@service.command(r"retweet " + TWEET_ID_REGEX + "$", mention=True)
@service.command(r"!(?:rt|retweet) " + TWEET_ID_REGEX + "$")
@requires_permission("tweet")
def retweet(ctx, id):
    """
    Retweet

    Retweets the specified tweet.
    """
    try:
        ctx.storage.api.statuses.retweet(id=id)
    except TwitterHTTPError as e:
        for error in e.response_data['errors']:
            ctx.respond("Twitter returned error: {}".format(error['message']))

@service.command(r"reply to " + TWEET_ID_REGEX + r"(?: with (?P<message>.+))?$", mention=True)
@service.command(r"!reply " + TWEET_ID_REGEX + r"(?: (?P<message>.+))?$")
@requires_permission("tweet")
def reply(ctx, id, message=None):
    """
    Reply

    Reply to the given tweet. Automatically prepends the appropriate @mention. If no message is given,
    attemps to search for a usable Brain service and uses it to generate a suitable reply.
    """
    api = ctx.storage.api

    try:
        tweet = api.statuses.show(id=id)
    except TwitterHTTPError:
        ctx.respond("Tweet {} does not exist!".format(id))
        return

    if message is None:
        try:
            brain = ctx.provider_for("brain")
        except KeyError:
            ctx.respond("No tweet provided and no Brain could be found!")
            return

        text = tweet["text"]
        message = brain(text, max_len=280)

    try:
        tweet = api.statuses.update(status=truncate(message), in_reply_to_status_id=id, auto_populate_reply_metadata=True)
        ctx.message("https://twitter.com/{0[user][screen_name]}/status/{0[id_str]}".format(tweet))
    except TwitterHTTPError as e:
        for error in e.response_data['errors']:
            ctx.respond("Twitter returned error: {}".format(error['message']))

@service.command(r"follow @?(?P<user>[0-9a-z_]+)", mention=True)
@requires_permission("tweet")
def follow(ctx, user):
    """
    Follow

    Follows a user.
    """
    api = ctx.storage.api
    try:
        api.friendships.create(screen_name=user, follow=True)
        ctx.respond("Now following @{}.".format(user))
    except TwitterHTTPError as e:
        for error in e.response_data['errors']:
            ctx.respond("Twitter returned error: {}".format(error['message']))

@service.command(r"(unfollow|stop following) @?(?P<user>[0-9a-z_]+)", mention=True)
@requires_permission("tweet")
def unfollow(ctx, user):
    """
    Unfollow

    Unfollows a user.
    """
    api = ctx.storage.api
    try:
        api.friendships.destroy(screen_name=user)
        ctx.respond("No longer following @{}.".format(user))
    except TwitterHTTPError as e:
        for error in e.response_data['errors']:
            ctx.respond("Twitter returned error: {}".format(error['message']))

# Truncate to max_length-3, breaking a word if the space-truncated string is
# less than this proportion of the maximum.
TRUNCATE_FORCE_BREAK_WORD_SPACE_THRESHOLD = 0.7
TRUNCATE_BREAK_POINTS = ' _-/'
def truncate(message, max_length=280):
    if len(message) > max_length:
        hard_max = message[:max_length]
        highest_break = max(hard_max.rfind(ch) for ch in TRUNCATE_BREAK_POINTS)
        truncated = message[:highest_break] + '...'
        # We don't really want to ...-truncate if it would look really silly
        if len(truncated) / float(max_length) < TRUNCATE_FORCE_BREAK_WORD_SPACE_THRESHOLD:
            message = message[:max_length-3] + '...'
        else:
            message = truncated
    return message
