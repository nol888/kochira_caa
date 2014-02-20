"""
A tool for children to learn how to spell.
"""

import re
from peewee import CharField

from kochira.db import Model

from kochira.service import Service
from kochira.auth import requires_permission

service = Service(__name__, __doc__)

class Correction(Model):
    word = CharField(50)
    replace = CharField(50)

    class Meta:
        indexes = (
            (("word",), True),
        )

@service.setup
def initialize_model(bot):
    Correction.create_table(True)


@service.command(r"forget how to spell (?P<word>.+)$", mention=True)
@requires_permission("american")
def remove_correction(ctx, word):
    """
    Add Correction

    Enables automatic spelling correction whenever someone says ``word``.
    """
    if not Correction.select().where(Correction.word == word).exists():
        ctx.respond("I'm not correcting \"{word}\".".format(
            word=word
        ))
        return

    Correction.delete().where(Correction.word == word).execute()

    ctx.respond("Okay, I won't correct the spelling of {word} anymore.".format(
        word=word
    ))


@service.hook("channel_message")
def do_correction(ctx, target, origin, message):
    message_lower = message.lower()

    for c in Correction.select():
        if c.word in message_lower:
            message = re.sub(re.escape(c.word), c.replace, message, flags=re.IGNORECASE)

    if message_lower == message.lower():
        return

    ctx.message("{origin} meant: {message}".format(
        origin=ctx.origin,
        message=message
    ))


@service.command(r"(?P<word>.+?) should be spelled (?P<replace>.+)$", mention=True)
@requires_permission("american")
def add_correction(ctx, word, replace):
    """
    Remove Correction

    Remove the correct spelling for ``word``.
    """
    if Correction.select().where(Correction.word == word).exists():
        ctx.respond("I'm already correcting the spelling of {word}.".format(
            word=word
        ))
        return

    Correction.create(word=word, replace=replace).save()

    ctx.respond("Okay, {word} should be {replace}.".format(
        word=word,
        replace=replace
    ))


@service.command(r"what can you spell\?$", mention=True)
def list_corrections(ctx):
    """
    List Corrections

    Lists all corrections.
    """
    ctx.respond("I know the correct spelling of: {things}".format(
        things=", ".join(x.word for x in Correction.select())
    ))
