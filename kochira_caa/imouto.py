"""
Say hello to imouto.

See the world from kedo's point of view.
"""
from kochira.service import Service
import re

service = Service(__name__, __doc__)

@service.command("!imouto(?: (?P<text>.+))?")
def imouto(ctx, text=None):
    """
    Imouto.

    Imouto-ify some text.
    """
    if text is None:
        if len(ctx.client.backlogs[ctx.target]) == 1:
            return

        _, text = ctx.client.backlogs[ctx.target][1]

    text = re.sub("\w\w\w\w+", "imouto", text)
    ctx.message(text)
