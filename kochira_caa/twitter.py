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

@service.config
class Config(Config):
    class OAuth(config.Config):
        consumer_key = config.Field(doc="Twitter API consumer key.")
        consumer_secret = config.Field(doc="Twitter API consumer secret.")
        token = config.Field(doc="Twitter API OAuth token.")
        token_secret = config.Field(doc="Twitter API OAuth token secret.")
    class Channel(config.Config):
        client = config.Field(doc="The client to announce on.")
        channel = config.Field(doc="The channel to announce on.")

    oauth = config.Field(doc="OAuth parameters.",
                         type=OAuth)
    announce = config.Field(doc="Places to announce tweets.",
                         type=config.Many(Channel))

@service.setup
def make_twitter(ctx):
    ctx.storage.api = Twitter(auth=twitter.OAuth(**ctx.config.oauth._fields))
    ctx.storage.active = True
    ctx.storage.last = None
    ctx.storage.stream = Thread(target=_follow_userstream, args=(ctx,), daemon=True)
    ctx.storage.stream.start()

@service.shutdown
def kill_twitter(ctx):
    ctx.storage.active = False
    ctx.storage.stream.join()

@service.command(r"tweet (?P<message>.+)$", mention=True)
@service.command(r"!tweet (?P<message>.+)$")
@requires_permission("tweet")
def tweet(ctx, message):
    """
    Tweet

    Tweet the given text.
    """
    ctx.storage.api.statuses.update(status=message)

@service.command(r"reply to (?P<id>[0-9]+|last)(?: with (?P<message>.+))?$", mention=True)
@service.command(r"!reply (?P<id>[0-9]+|last)(?: (?P<message>.+))?$")
@requires_permission("tweet")
def reply(ctx, id, message=None):
    """
    Reply

    Reply to the given tweet. Automatically prepends the appropriate @mention. If no tweet is given,
    attemps to search for a usable Brain service and uses it to generate a suitable reply.
    """
    api = ctx.storage.api

    if id == "last":
        if ctx.storage.last is None:
            ctx.client.message(ctx.target, "{origin}: I haven't seen any tweets yet!".format(
                origin=ctx.origin
            ))
            return

        id = ctx.storage.last["id_str"]

    try:
        tweet = api.statuses.show(id=id)
    except TwitterHTTPError:
        ctx.respond("{origin}: Tweet {id} does not exist!".format(
            origin=ctx.origin,
            id=id
        ))
        return

    if message is None:
        brain = _find_brain(ctx.bot)
        if brain is None:
            ctx.respond("{origin}: No tweet provided and no Brain could be found!".format(
                origin=ctx.origin
            ))
            return

        text = tweet["text"]
        user = "@{} ".format(tweet["user"]["screen_name"])
        message = user + brain.reply(ctx.bot, text, max_len=140-len(user))
    else:
        message = "@{} {}".format(tweet["user"]["screen_name"], message)

    api.statuses.update(status=message, in_reply_to_status_id=id)

def _follow_userstream(ctx):
    o = ctx.config.oauth._fields
    stream = TwitterStream(auth=twitter.OAuth(**o), domain="userstream.twitter.com", block=False)

    for msg in stream.user():
        if msg is not None:
            service.logger.debug(str(msg))

            # Twitter signals start of stream with the "friends" message.
            if 'friends' in msg:
                _announce(ctx, "\x02twitter:\x02 This channel is now streaming Twitter in real-time.")
            elif 'text' in msg and 'user' in msg:
                ctx.storage.last = msg

                url_format = "(https://twitter.com/{0[user][screen_name]}/status/{0[id_str]})"
                if 'retweeted_status' in msg:
                    text = "\x02[@{0[user][screen_name]} RT @{0[retweeted_status][user][screen_name]}]\x02 {0[retweeted_status][text]} " + url_format
                else:
                    text = "\x02[@{0[user][screen_name]}]\x02 {0[text]} " + url_format

                _announce(ctx, text.format(msg))
        else:
            time.sleep(.5)

        if not ctx.storage.active:
            return

def _announce(ctx, text):
    for announce in ctx.config.announce:
        if announce.client in ctx.bot.clients:
            ctx.bot.clients[announce.client].message(announce.channel, text)

def _find_brain(bot):
    import importlib

    if "kochira.services.textproc.brain" in bot.services:
        return importlib.import_module("kochira.services.textproc.brain")

    for name, _ in bot.services.items():
        if 'brain' in name.lower():
            service = importlib.import_module(name)
            if callable(getattr(service, 'reply', None)):
                return service

    return None
