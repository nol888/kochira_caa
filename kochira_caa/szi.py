"""
SZI module

Keeps track of how often SZI is being dumb.
"""

import humanize
from datetime import datetime

from kochira.service import Service

service = Service(__name__, __doc__)

last_smugleaf = None

@service.command(r"(?:how long has it been since szi(?: was)?|when was szi last|when did szi last) (?:a faggot|(?:(?:mention(?:ed)?|fug(?:ged)?|say|said) )?smugleaf)$", mention=True)
def query_last_smugleaf(ctx):
    """
    Smugleaf query.

    Ask Kochira the last time SZI last said "smugleaf".
    """
    if last_smugleaf:
        time_since_smugleaf = datetime.utcnow() - last_smugleaf
        ctx.respond("It has been {duration} since SZI last fugleafed.".format(
            duration=humanize.naturaltime(time_since_smugleaf)
        ))
    else:
        ctx.respond(":thinking_mawaru_3d_backward: SZI has yet to mention smugleaf :thinking_mawaru_3d_forward:")

@service.hook("channel_message")
def update_last_smugleaf(ctx, target, origin, message):
    if origin.lower() == 'szi':
        if 'smugleaf' in message:
            global last_smugleaf
            last_smugleaf = datetime.utcnow()
