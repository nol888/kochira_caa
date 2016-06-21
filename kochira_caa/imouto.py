"""
Say hello to imouto.

See the world from kedo's point of view.
"""
from kochira.service import Service
from nltk.stem.snowball import SnowballStemmer
import re

stemmer = SnowballStemmer('english')

service = Service(__name__, __doc__)

@service.command("!imouto(?: (?P<text>.+))?")
def imouto(ctx, text=None):
    """
    Imouto.

    Imouto-ify some text.
    """
    if text is None:
        if len(ctx.client.backlogs[ctx.target]) == 1:
            return

        _, text = ctx.client.backlogs[ctx.target][1]

    def case_corrected_imouto(word):
        if all(c.isupper() for c in word):
            return 'IMOUTO'

        if word.capitalize() == word:
            return 'Imouto'

        return 'imouto'

    def stemmed_imouto(match):
        word = match.group(0)
        word_stem = stemmer.stem(word)
        if word != word_stem and word.startswith(word_stem):
            return case_corrected_imouto(word) + word[len(word_stem):]
        else:
            return case_corrected_imouto(word)

    text = re.sub("\w\w\w\w+", stemmed_imouto, text)
    ctx.message(text)
