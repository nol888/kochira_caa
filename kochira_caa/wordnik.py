"""
Wordnik API.

For when you want to do terrible things with words.
"""
import requests

from kochira import config
from kochira.service import Service, background, Config

service = Service(__name__, __doc__)

@service.command(r"^:amatsukaze:$")
@background
def amatsukaze(ctx):
    """
    :amatsukaze:

    That's surely very advanced for computers.
    """
    adjective = requests.get("http://api.wordnik.com/v4/words.json/randomWord", params={
        'hasDictionaryDef': 'false',
        'includePartOfSpeech': 'adjective',
        'minCorpusCount': 1000,
        'minLength': 5,
        'api_key': 'a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5',
    }).json()['word']
    noun = requests.get("http://api.wordnik.com/v4/words.json/randomWord", params={
        'hasDictionaryDef': 'true',
        'includePartOfSpeech': 'noun',
        'minCorpusCount': 1000,
        'minLength': 5,
        'api_key': 'a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5',
    }).json()['word']

    ctx.message("That's surely very {adjective} for {noun}.".format(
        adjective=adjective,
        noun=noun,
    ))

