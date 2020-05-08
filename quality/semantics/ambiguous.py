import os
import sys

from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)))
from nltk import sent_tokenize, RegexpTokenizer
from core.tree import TreeParser

# for debug
import pandas as pd


def ambiguous(data, debug=False):
    for datum in tqdm(data):
        essay = datum['essay']
        sentences = sent_tokenize(essay)

        # setup tree parser
        parser = TreeParser()
        parser.setup()

        print('Parser')
        print(parser.parser)

        # parse sentences
        for sentence in sentences:

            forest = parser.parse(sentence)
            for tree in forest:
                tree.pretty_print()


# if __name__ == '__main__':
#     test_corpora = pd.read_excel('data\\quality_data\\quality_data.xlsx')
#     for test_corpus in test_corpora['essay']:
#         ambiguous(test_corpus, debug=True)
#         break
