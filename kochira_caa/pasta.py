import nltk
import re
from kochira import config
from kochira.service import Service, Config
from markovify.text import NewlineText

service = Service(__name__, __doc__)


@service.config
class Config(Config):
    model_file = config.Field(doc="Location where the model file is stored", default="pasta_model.json")


class POSifiedText(NewlineText):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = filter(lambda x: bool(x), words)
        words = ["::".join(tag) for tag in nltk.pos_tag(words)]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


@service.setup
def load_model(ctx):
    with open(ctx.config.model_file, 'r') as f:
        ctx.storage.model = POSifiedText.from_chain(f.read())


@service.command('!pasta')
def generate_pasta(ctx):
    """
    🐸♊️🐸♊️🐸♊️🐸♊️🐸♊️ good memes go౦ԁ mEmes
    """
    ctx.message(ctx.storage.model.make_sentence())


if __name__ == '__main__':
    import sys

    with open(sys.argv[1], 'r') as f:
        corpus = f.read()

    pasta_model = POSifiedText(corpus)

    with open(sys.argv[2], 'w') as f:
        f.write(pasta_model.chain.to_json())

