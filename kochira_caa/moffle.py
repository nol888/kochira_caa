"""
Moffle search.

For when you really want context.
"""
import hmac
import requests
from base64 import urlsafe_b64encode
from hashlib import sha256
from itertools import count, compress
from urllib.parse import quote_plus, unquote_plus

from kochira import config
from kochira.service import Service, background, Config

service = Service(__name__, __doc__)

@service.config
class MoffleConfig(Config):
    class Instance(Config):
        base_url = config.Field(doc="Base URL of the Moffle instance.")
        api_uid = config.Field(doc="UID for API authentication.")
        api_key = config.Field(doc="Key for API authentication.")
    instances = config.Field(doc="Moffle instances keyed by name.", type=config.Mapping(Instance))

def sign_request(key, path, args):
    path = unquote_plus(path).encode('utf_8') + b'?'
    args = '&'.join(sorted(["{}={}".format(k, v) for k, v in args.items()])).encode('utf_8')

    m = hmac.new(key.encode('utf_8'), digestmod=sha256)
    m.update(path)
    m.update(args)
    return urlsafe_b64encode(m.digest())

def _search(instance, network, channel, text):
    path = '/api/search/{network}/{channel}'.format(
        network=quote_plus(network),
        channel=quote_plus(channel)
    )
    args = {'q': text, 'uid': instance.api_uid}
    args.update({'sig': sign_request(instance.api_key, path, args)})
    result = requests.get(instance.base_url.rstrip('/') + path, params=args)
    result.raise_for_status()
    return result.json()

@service.command(r"search (?P<instance>\w+) for (?P<text>.+)$", mention=True)
@background
def search(ctx, instance, text):
    """
    Search

    Searches a Moffle instance for things.
    """
    instance = instance.lower()
    if not instance in ctx.config.instances:
        ctx.respond("I don't know what \"{instance}\" is!".format(instance=instance))
        return
    instance = ctx.config.instances[instance]

    r = _search(instance, ctx.client.name.lower(), ctx.target.lower(), text)
    result = r['results'][1]
    match_idx = list(compress(count(), [1 if line['line_marker'] == ':' else 0 for line in result['lines']]))[0]
    lines = result['lines'][max(0, match_idx-2):min(match_idx+3, len(result['lines']))]

    for line in lines:
        ctx.message(line['line'])
    ctx.message("\x02Log from:\x02 {date}. \x02Total results:\x02 {total}. {base}{path}".format(
        date=result['date'],
        total=r['total_results'],
        base=instance.base_url.rstrip('/'),
        path=r['canonical_url']
    ))
