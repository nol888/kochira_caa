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

def load_brain(ctx):
    ctx.storage.brains[ctx.config.brain_file] = Brain(ctx.config.brain_file, check_same_thread=False)
    ctx.storage.brains[ctx.config.brain_file].scorer.add_scorer(2.0, LengthScorer())

@service.setup
def load_default_brain(ctx):
    ctx.storage.brains = {}
    load_brain(ctx)
    ctx.storage.brain = ctx.storage.brains[ctx.config.brain_file]

@service.shutdown
def unload_brain(ctx):
    for brain in ctx.storage.brains:
        brain.graph.close()

def get_brain(ctx):
    if ctx.config.brain_file not in ctx.storage.brains:
        load_brain(ctx)
    return ctx.storage.brains[ctx.config.brain_file]

@service.hook("channel_message", priority=-9999)
@background
def reply_and_learn(ctx, target, origin, message):
    front, _, rest = message.partition(" ")

    mention = False
    reply = False

    if front.strip(",:").lower() == ctx.client.nickname.lower():
        mention = True
        reply = True
        message = rest

    message = message.strip()
    brain = get_brain(ctx)

    if re.search(r"\b{}\b".format(re.escape(ctx.client.nickname)), message, re.I) is not None:
        reply = True

    if reply:
        reply_message = brain.reply(message)

        if mention:
            ctx.respond(reply_message)
        else:
            ctx.message(reply_message)

    if message:
        brain.learn(message)

@service.provides("brain")
def reply(ctx, message, *args, **kwargs):
    return service.binding_for(ctx.bot).storage.brain.reply(message, *args, **kwargs)

