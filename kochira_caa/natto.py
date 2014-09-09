"""
nattobrain pkls go
"""

from kochira.service import Service, background
from cobe.brain import Brain

service = Service(__name__, __doc__)

@service.setup
def load_brain(ctx):
    ctx.storage.brain = Brain("natto.db", check_same_thread=False)

@service.shutdown
def unload_brain(ctx):
    ctx.storage.brain.graph.close()

@service.command(r":natto:", mention=False)
@background
def generate_natto(ctx):
    ctx.message('<nattofriends> {}'.format(ctx.storage.brain.reply('')))

