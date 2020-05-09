from csv import DictReader
from nltk import sent_tokenize
from nltk.parse.corenlp import CoreNLPServer, CoreNLPParser
from os import path

import settings


class TreeParser:
    def __init__(self):
        self.parser = None

    def setup(self):
        url = settings.CORENLP_URL

        if url is None:
            server = CoreNLPServer(
               settings.CORENLP_PATH,
               settings.CORENLP_MODEL_PATH,
            )

            server.start()

            url = server.url

        self.parser = CoreNLPParser(url=url)
        return self.parser

    def parse(self, sentence):
        if not self.parser:
            raise AttributeError('parser is not set up')

        return self.parser.raw_parse(sentence)


if __name__ == '__main__':
    parser = TreeParser()
    parser.setup()
    print("Loaded :D")

    with open('data/quality_data/quality_data.csv', encoding='utf-8') as f:
        reader = DictReader(f)

        for row in list(reader)[:1]:
            sents = sent_tokenize(row['essay'])

            for sent in sents:
                forest = parser.parse(sent)
                for tree in forest:
                    tree.pretty_print()
