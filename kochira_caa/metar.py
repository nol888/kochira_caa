"""
METAR/TAF fetcher.

For SZI and SZI accessories.
"""

import requests

from kochira.service import Service

service = Service(__name__, __doc__)

@service.command(r"!metar (?P<location>[A-Z0-9]{4})$")
def metar(ctx, location):
    """
    METAR

    Get the METAR for a specific station by ICAO ident.
    """
    response = requests.get(
        "https://avwx.rest/api/preview/metar/{location}".format(location=location),
        params={
            'format': 'json',
            'onfail': 'cache',
        },
    ).json()

    ctx.respond(response['sanitized'])

