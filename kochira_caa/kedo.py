"""
kedo module.

Allows mortals to learn from the tome of kedo.
"""

import re

from random import choice, randint, random

from peewee import CharField, fn

from kochira.auth import requires_permission
from kochira.db import Model
from kochira.service import Service

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
def kedo(ctx, topic):
    """
    kedo

    Query the tome of kedo and return the results.
    """
    if not KedoBit.select().where(KedoBit.topic == topic).exists():
        ctx.respond("kedo hasn't said anything about {topic} yet. poop.".format(
            topic=topic
        ))
        return

    ctx.message("\x02kedo on {topic}:\x02 {bit.knowledge}".format(
        topic=topic,
        bit=KedoBit.select().where(KedoBit.topic == topic).order_by(fn.Random()).limit(1)[0]))

@service.command(r"kedo on (?P<topic>.*\w)\s*: (?P<knowledge>.+)$", mention=True)
@service.command(r"!kedolearn (?P<topic>.+) : (?P<knowledge>.+)$")
@requires_permission("kedo")
def kedo_learn(ctx, topic, knowledge):
    """
    kedolearn

    Instill new knowledge into the tome of kedo. Multiple entries on the
    same topic are allowed.
    """
    KedoBit.create(topic=topic, knowledge=knowledge).save()

    ctx.respond("kedo now knows about \x02{topic}\x02!".format(topic=topic))

@service.command(r"kedo no longer speaks of (?P<topic>.+)$", mention=True)
@service.command(r"!kedoforget (?P<topic>.+)$")
@requires_permission("kedo")
def kedo_forget(ctx, topic):
    """
    kedoforget

    Erase gospel from the tome of kedo. If multiple entries had been stored under
    the same topic, they are all removed.
    """
    KedoBit.delete().where(KedoBit.topic == topic).execute()

    ctx.respond("kedo no longer knows about \x02{topic}\x02.".format(topic=topic))

@service.command(r"what does kedo know about\??$", mention=True)
@service.command(r"!kedo$")
def kedolist(ctx):
    """
    kedolist

    List all scripture in the book of kedo.
    """
    ctx.message("\x02kedo knows about:\x02 {things}".format(
        things=", ".join([x.topic for x in KedoBit.select().group_by(KedoBit.topic)])
    ))

@service.command(r".*\[in\].*")
def lnkd_simulator_2016(ctx):
    """
    LNKD simulator 2016

    Accurate simulation of LNKD.
    """
    ctx.respond("\x02LNKD\x02 down {percent}%!".format(
        percent=randint(15, 45)
    ))

@service.command(r"!nichi(?: (?P<text>.+))?")
def nichi(ctx, text=None):
    """
    ,,,n,ic,,,hi
    """
    if text is None:
        if len(ctx.client.backlogs[ctx.target]) == 1:
            return

        _, text = ctx.client.backlogs[ctx.target][1]

    new_text = ''
    for c in text:
        if random() < 0.4:
            if random() < 0.3:
                new_text += ',' * randint(3,6)
            else:
                new_text += ',' * randint(1,2)
        new_text += c
    ctx.message(new_text)

RIN_REGEX = re.compile(r"(?:\b([A-Za-z0-9_'-]+) )?\b([A-Za-z0-9_'-]+) in([A-Za-z0-9_-]+)")
RIN_IGNORE = set(['to', 'ternet'])

@service.hook("channel_message")
def rin(ctx, target, origin, message):
    """
    <kedo> nice rinnovation! xDD
    """
    ins = RIN_REGEX.findall(message)
    if ins and random() < 0.5:
        far_prev, prev, in_word = choice(ins)

        if in_word not in RIN_IGNORE:
            prev = (far_prev + ' ' + prev) if far_prev and random() < 0.4 else prev
            ctx.message("<kedo> {} rin{} xDD".format(prev, in_word))

