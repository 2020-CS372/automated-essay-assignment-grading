import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)))
from nltk import sent_tokenize, RegexpTokenizer
from core.tree import TreeParser

# for debug
import pandas as pd


def ambiguous(corpus=None, debug=False):
    # tokenizing sentence
    sentences = sent_tokenize(corpus)

    # setup tree parser
    parser = TreeParser()
    parser.setup(corpus)

    print('Parser')
    print(parser.parser)
    
    print('Productions')
    print(len(parser.productions))

    # parse sentences
    for sentence in sentences:
        print(sentence)
        res = parser.parse_sentence(sentence)

        print(list(res))

        # forest = parser.parse(sentence)
        # for tree in forest:
        #     tree.pretty_print()


if __name__ == '__main__':
    test_corpora = pd.read_excel('data\\quality_data\\quality_data.xlsx')
    for test_corpus in test_corpora['essay']:
        ambiguous(test_corpus, debug=True)
        break
