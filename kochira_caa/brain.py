"""
Artificial (un)intelligence.

Allows the bot to reply whenever its nickname is mentioned.
"""

import re

from kochira import config
from kochira.service import Service, background, Config
from cobe.brain import Brain
from cobe.scoring import LengthScorer

service = Service(__name__, __doc__)

@service.config
class Config(Config):
    brain_file = config.Field(doc="Location to store the brain in.", default="brain.db")


@service.setup
def load_brain(bot):
    config = service.config_for(bot)
    storage = service.storage_for(bot)

    storage.brain = Brain(config.brain_file, check_same_thread=False)
    storage.brain.scorer.add_scorer(2.0, LengthScorer())

@service.shutdown
def unload_brain(bot):
    storage = service.storage_for(bot)

    storage.brain.graph.close()


@service.hook("channel_message", priority=-9999)
@background
def reply_and_learn(client, target, origin, message):
    storage = service.storage_for(client.bot)

    front, _, rest = message.partition(" ")

    mention = False
    reply = False

    if front.strip(",:").lower() == client.nickname.lower():
        mention = True
        reply = True
        message = rest

    message = message.strip()

    if re.search(r"\b{}\b".format(re.escape(client.nickname)), message, re.I) is not None:
        reply = True

    if reply:
        reply_message = storage.brain.reply(message)

        if mention:
            client.message(target, "{origin}: {message}".format(origin=origin, message=reply_message))
        else:
            client.message(target, reply_message)

    if message:
        storage.brain.learn(message)

def reply(bot, message, *args, **kwargs):
    return service.storage_for(bot).brain.reply(message, *args, **kwargs)

