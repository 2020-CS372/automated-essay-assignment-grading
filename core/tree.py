from nltk import induce_pcfg, pos_tag
from nltk.corpus import treebank
from nltk.grammar import Nonterminal, Production
from nltk.parse import ViterbiParser
from nltk.tokenize import sent_tokenize, word_tokenize
from tqdm.autonotebook import tqdm


class TreeParser:
    def __init__(self):
        self.parser = None
        self.productions = []

        for item in tqdm(treebank.fileids()):
            for tree in treebank.parsed_sents(item):
                tree.collapse_unary(collapsePOS = False)
                tree.chomsky_normal_form(horzMarkov = 2)
                self.productions += tree.productions()

    def setup(self, corpus):
        sentences = sent_tokenize(corpus)
        custom_productions = self.productions[:]

        for sentence in sentences:
            tokens = word_tokenize(sentence)
            tags = pos_tag(tokens)
            for text, pos in tags:
                custom_productions.append(
                    Production(Nonterminal(pos), (text, ))
                )

        grammar = induce_pcfg(Nonterminal('S'), custom_productions)
        self.parser = ViterbiParser(grammar)

        return self.parser

    def parse(self, sentence):
        if not self.parser:
            raise AttributeError('parser is not set up')

        return self.parser.parse(word_tokenize(sentence))


if __name__ == '__main__':
    sentences = """
    I love you.
    I like you.
    """

    parser = TreeParser()
    parser.setup(sentences)

    forest = parser.parse('I love you.')
    for tree in forest:
        tree.pretty_print()
