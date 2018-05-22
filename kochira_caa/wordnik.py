"""
Wordnik API.

For when you want to do terrible things with words.
"""
import requests

from kochira import config
from kochira.service import Service, background, Config

service = Service(__name__, __doc__)

@service.config
class Config(Config):
    api_key = config.Field(doc="Wordnik API key")

@service.setup
def make_api(ctx):
    def wordnik_get_word(part_of_speech, min_corpus_count=1000):
        return requests.get("http://api.wordnik.com/v4/words.json/randomWord", params={
            'hasDictionaryDef': 'true',
            'includePartOfSpeech': part_of_speech,
            'minCorpusCount': min_corpus_count,
            'minLength': 5,
            'api_key': ctx.config.api_key,
        }).json()['word']

    ctx.storage.get_word = wordnik_get_word

@service.command(r"^:amatsukaze:$")
@background
def amatsukaze(ctx):
    """
    :amatsukaze:

    That's surely very advanced for computers.
    """
    adjective = ctx.storage.get_word('adjective')
    noun = ctx.storage.get_word('noun')

    ctx.message("That's surely very {adjective} for {noun}.".format(
        adjective=adjective,
        noun=noun,
    ))

@service.command(r"^:szi:$")
@background
def szi(ctx):
    """
    :szi:

    <szi> Choose this, whips out axiom of choice
    """
    verb = ctx.storage.get_word('verb-transitive')
    noun = ctx.storage.get_word('noun')

    ctx.message("<szi> {verb} this, whips out {noun}".format(
        verb=verb,
        noun=noun,
    ))

@service.command(r"^(\w+ )((on|onto|in|at|out|for|to|by|off|about) )?this$")
@background
def szi_partial(ctx):
    """
    autism on this

    <szi> bring this <szi> whips out your deliverance from a startup that won't make money
    """
    noun = ctx.storage.get_word('noun')

    ctx.message("whips out {noun}".format(
        noun=noun
    ))

