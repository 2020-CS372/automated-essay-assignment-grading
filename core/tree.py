from csv import DictReader
from nltk.parse.corenlp import CoreNLPServer, CoreNLPParser


class TreeParser:
    def __init__(self):
        self.parser = None

    def setup(self, url = None):
        if url is None:
            server = CoreNLPServer(
               "./data/corenlp/stanford-corenlp-4.0.0.jar",
               "./data/corenlp/stanford-corenlp-4.0.0-models.jar",
            )

            server.start()

            url = 'http://localhost:9000'

        self.parser = CoreNLPParser(url=url)
        return self.parser

    def parse(self, sentence):
        if not self.parser:
            raise AttributeError('parser is not set up')

        return self.parser.raw_parse(sentence)


if __name__ == '__main__':
    parser = TreeParser()
    parser.setup('http://localhost:12366')
    print("Loaded :D")

    with open('data/quality_data/quality_data.csv', encoding='utf-8') as f:
        reader = DictReader(f)

        for row in list(reader)[:1]:
            forest = parser.parse(row['essay'])
            for tree in forest:
                tree.pretty_print()
