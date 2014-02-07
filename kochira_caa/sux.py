from kochira.service import Service

service = Service(__name__, __doc__)

@service.command(r"!sux (?P<what>.+)$")
def sux(client, target, origin, what):
       client.message(target, "fuck {what}; {what} sucks; {what} is dying; {what} is dead to me; {what} hit wtc".format(what=what))

