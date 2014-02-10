"""
Say hello to imouto.

See the world from kedo's point of view.
"""
from kochira.service import Service
import re

service = Service(__name__, __doc__)

@service.command("!imouto(?: (?P<text>.+))?")
def imouto(client, target, origin, text=None):
    """
    Imouto.

    Imouto-ify some text.
    """
    if text is None:
        if len(client.backlogs[target]) == 1:
            return

        _, text = client.backlogs[target][1]

    text = re.sub("\w\w\w\w+", "imouto", text)
    client.message(target, text)
