from core.tree import TreeParser
from csv import DictReader
from nltk import sent_tokenize, RegexpTokenizer


CLAUSES_INTRODUCED = ('SBAR', 'SBARQ')
CLAUSES_DECLARATIVE = ('S', 'SINV', 'SQ')
CLAUSES = CLAUSES_INTRODUCED + CLAUSES_DECLARATIVE

CONJUNCTIONS = ('CC', 'IN', ',')

VERBS = ('VB', 'VBD', 'VBP', 'VBZ')

def structure(input_data):
    corpora = [input_dict['essay'] for input_dict in input_data]

    for corpus in corpora:
        sents = sent_tokenize(corpus)

        parser = TreeParser()
        parser.setup()

        for sent_index, sent in enumerate(sents):
            tree = next(parser.parse(sent))

            main_elem = tree[0]
            if main_elem.label() not in CLAUSES:
                print("No root-level clause: %s / %s" % (main_elem.label(), sent))
                continue

            tree.pretty_print()
            # traverse_tree(main_elem)


def stringify_tree(subtree):
    if type(subtree) == str:
        return subtree

    content = []
    for next_subtree in subtree:
        content.append(stringify_tree(next_subtree))

    return ' '.join(content)


def traverse_tree(subtree):
    if type(subtree) == str:
        return

    if subtree.label() in CLAUSES_DECLARATIVE:
        verb_count = 0
        bypass_check = False

        for next_subtree in subtree:
            if next_subtree.label() == 'VP' or next_subtree.label() in VERBS:
                verb_count += 1

            if next_subtree.label() in CONJUNCTIONS:
                bypass_check = True
                break

        if not bypass_check and verb_count != 1:
            print("Clause doesn't have exactly 1 verb phrase: %s" % stringify_tree(subtree))

    for next_subtree in subtree:
        traverse_tree(next_subtree)


if __name__ == '__main__':
    text_amount = 1

    with open('data/quality_data/quality_data.csv') as f:
        reader = DictReader(f)

        for row in reader[:test_amount]:
            structure(row['essay'])
