"""
kedo module.

Allows mortals to learn from the tome of kedo.
"""

from peewee import CharField, fn

from kochira.db import Model

from kochira.service import Service
from kochira.auth import requires_permission

service = Service(__name__, __doc__)

class KedoBit(Model):
    topic = CharField(255)
    knowledge = CharField(450)

    class Meta:
        indexes = (
            (("topic",), False),
        )

@service.setup
def initialize_model(bot):
    KedoBit.create_table(True)

@service.command(r"kedo on (?P<topic>[^:]+)$", mention=True)
@service.command(r"!kedo (?P<topic>.+)$")
def kedo(client, target, origin, topic):
    """
    kedo

    Query the tome of kedo and return the results.
    """
    if not KedoBit.select().where(KedoBit.topic == topic).exists():
        client.message(target, "{origin}: kedo hasn't said anything about {topic} yet. poop.".format(
            origin=origin,
            topic=topic
        ))
        return

    client.message(target, "\x02kedo on {topic}:\x02 {bit.knowledge}".format(
        topic=topic,
        bit=KedoBit.select().where(KedoBit.topic == topic).order_by(fn.Random()).limit(1)[0]))

@service.command(r"kedo on (?P<topic>.+): (?P<knowledge>.+)$", mention=True)
@service.command(r"!kedolearn (?P<topic>.+) : (?P<knowledge>.+)$")
@requires_permission("kedo")
def kedo_learn(client, target, origin, topic, knowledge):
    """
    kedolearn

    Instill new knowledge into the tome of kedo. Multiple entries on the
    same topic are allowed.
    """
    KedoBit.create(topic=topic, knowledge=knowledge).save()

    client.message(target, "kedo now knows about \x02{topic}\x02!".format(topic=topic))

@service.command(r"kedo no longer speaks of (?P<topic>.+)$", mention=True)
@service.command(r"!kedoforget (?P<topic>.+)$")
@requires_permission("kedo")
def kedo_forget(client, target, origin, topic):
    """
    kedoforget

    Erase gospel from the tome of kedo. If multiple entries had been stored under
    the same topic, they are all removed.
    """
    KedoBit.delete().where(KedoBit.topic == topic).execute()

    client.message(target, "kedo no longer knows about \x02{topic}\x02.".format(topic=topic))

@service.command(r"what does kedo know about\??$", mention=True)
@service.command(r"!kedo$")
def kedolist(client, target, origin):
    """
    kedolist

    List all scripture in the book of kedo.
    """
    client.message(target, "\x02kedo knows about:\x02 {things}".format(
        things=", ".join([x.topic for x in KedoBit.select().group_by(KedoBit.topic)])
    ))

