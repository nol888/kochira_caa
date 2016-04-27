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

    def case_corrected_imouto(match):
        if all(c.isupper() for c in match.group(0)):
            return 'IMOUTO'

        if all(c.islower() for c in match.group(0)):
            return 'imouto'

        if match.group(0).capitalize() == match.group(0):
            return 'Imouto'

    text = re.sub("\w\w\w\w+", case_corrected_imouto, text)
    ctx.message(text)
