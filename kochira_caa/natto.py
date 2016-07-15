"""
nattobrain pkls go
"""

from random import random

from kochira.service import Service, background
from cobe.brain import Brain

service = Service(__name__, __doc__)

@service.setup
def load_brain(ctx):
    ctx.storage.brain = Brain("natto.db", check_same_thread=False)
    ctx.storage.adrei = Brain("a-drei.db", check_same_thread=False)

@service.shutdown
def unload_brain(ctx):
    ctx.storage.brain.graph.close()
    ctx.storage.adrei.graph.close()

@service.command(r":natto:", mention=False)
@background
def generate_natto(ctx):
    msg = ctx.storage.brain.reply('')
    if random() < 0.2:
        ctx.message('<nattofriends> ' + msg[:-1])
        ctx.message('<nattofriends> ' + msg[-1])
    else:
        ctx.message('<nattofriends> ' + msg)

@service.command(r":a-drei:", mention=False)
@background
def generate_adrei(ctx):
    ctx.message('\x02[@cute_hospital]\x02 ' + ctx.storage.adrei.reply(''))
