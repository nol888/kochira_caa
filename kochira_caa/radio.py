import requests

from kochira.auth import requires_permission
from kochira.service import Service, background
from lxml import etree

service = Service(__name__, __doc__)

def _np(bot):
    config = service.config_for(bot)
    mount = config["mount"]
    r = etree.fromstring(requests.get(config["url"], auth=(config["username"], config["password"])).content)

    mount_exists = bool(r.xpath("source[@mount='{}']".format(mount)))
    artist = r.xpath("source[@mount='{}']/artist/text()".format(mount))
    title = r.xpath("source[@mount='{}']/title/text()".format(mount))

    if not mount_exists:
        return None
    return (artist[0] if artist else "", title[0] if title else "")

@service.command("^\.np$")
@requires_permission("caa_radio")
@background
def now_playing(client, target, origin):
    np = _np(client.bot)
    if not np:
        client.message(target, "\x02Now playing:\x02 Nothing!")
    elif np == ("", ""):
        client.message(target, "\x02Now playing:\x02 No metadata available!")
    else:
        client.message(target, "\x02Now playing:\x02 {}".format(" - ".join(np)))
