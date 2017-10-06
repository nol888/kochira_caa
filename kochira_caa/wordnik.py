"""
Wordnik API.

For when you want to do terrible things with words.
"""
import requests

from kochira import config
from kochira.service import Service, background, Config

service = Service(__name__, __doc__)

def wordnik_get_word(part_of_speech,  min_corpus_count=1000):
    return requests.get("http://api.wordnik.com/v4/words.json/randomWord", params={
        'hasDictionaryDef': 'true',
        'includePartOfSpeech': part_of_speech,
        'minCorpusCount': min_corpus_count,
        'minLength': 5,
        'api_key': 'a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5',
    }).json()['word']

@service.command(r"^:amatsukaze:$")
@background
def amatsukaze(ctx):
    """
    :amatsukaze:

    That's surely very advanced for computers.
    """
    adjective = wordnik_get_word('adjective')
    noun = wordnik_get_word('noun')

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
    verb = wordnik_get_word('verb-transitive')
    noun = wordnik_get_word('noun')

    ctx.message("<szi> {verb} this, whips out {noun}".format(
        verb=verb,
        noun=noun,
    ))
