"""
LONDON
O
N
D
O
N
"""

from kochira.service import Service

service = Service(__name__, __doc__)

@service.command(r"!london(?: (?P<what>.{1,10}))?$")
def london(ctx, what=None):
    if what is None:
        if len(ctx.client.backlogs[ctx.target]) == 1 or len(ctx.client.backlogs[ctx.target][1][1]) > 10:
            return

        _, what = ctx.client.backlogs[ctx.target][1]
    ctx.message(what.upper())
    for x in what.upper()[1:]:
        ctx.message(x)

