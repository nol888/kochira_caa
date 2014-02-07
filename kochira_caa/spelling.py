"""
A tool for children to learn how to spell.

Configuration Options
=====================
None.

Commands
========

Add Correction
--------------

::

    $bot: <word> should be spelled <correct_word>

**Requires permission:** american

Enables automatic spelling correction whenever someone says ``word``.

Remove Correction
-----------------

::

    $bot: forget how to spell <word>

**Requires permission:** american

Remove the correct spelling for ``word``.
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
def remove_correction(client, target, origin, word):
    if not Correction.select().where(Correction.word == word).exists():
        client.message(target, "{origin}: I'm not correcting \"{word}\".".format(
            origin=origin,
            word=word
        ))
        return

    Correction.delete().where(Correction.word == word).execute()

    client.message(target, "{origin}: Okay, I won't correct the spelling of {word} anymore.".format(
        origin=origin,
        word=word
    ))


@service.hook("channel_message")
def do_correction(client, target, origin, message):
    message_lower = message.lower()

    for c in Correction.select():
        if c.word in message_lower:
            message = re.sub(re.escape(c.word), c.replace, message, flags=re.IGNORECASE)

    if message_lower == message.lower():
        return

    client.message(target, "{origin} meant: {message}".format(
        origin=origin,
        message=message
    ))


@service.command(r"(?P<word>.+?) should be spelled (?P<replace>.+)$", mention=True)
@requires_permission("american")
def add_correction(client, target, origin, word, replace):
    if Correction.select().where(Correction.word == word).exists():
        client.message(target, "{origin}: I'm already correcting the spelling of {word}.".format(
            origin=origin,
            word=word
        ))
        return

    Correction.create(word=word, replace=replace).save()

    client.message(target, "{origin}: Okay, {word} should be {replace}.".format(
        origin=origin,
        word=word,
        replace=replace
    ))

