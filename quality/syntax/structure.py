from core.tree import TreeParser
from csv import DictReader
from nltk import sent_tokenize, RegexpTokenizer


def structure(input_data):
    sents = sent_tokenize(input_data)

    parser = TreeParser()
    parser.setup(sents)

    score = 0
    for sent_index, sent in enumerate(sents):
        tree = parser.parse_one(sent)

        # Check whether there is only one root-level subject
        if not tree:
            print("No root-level subject, or structure is enable to parse at sent #%d" % sent_index)
            score -= 1

            continue

        # Check whether there is only one root-level verb
        def verb_count(subtree):
            if subtree.label() in ('VB', 'VBD', 'VBP', 'VBZ'):
                return 1 + sum([find_verb(next_tree) for next_tree in subtree])

            # Don't check if it is not root-level verb
            if 'CLR' in subtree.label():
                return 0

        if verb_count(tree) != 1:
            print("Not exactly one root-level verb presented at sent #%d" % sent_index)
            score -= 1

            continue

        # (Optional) Check if the arguments which root-level verb takes are propery given (ex. Objectives)

    return score


if __name__ == '__main__':
    text_amount = 1

    with open('data/quality_data/quality_data.csv') as f:
        reader = DictReader(f)

        for row in reader[:test_amount]:
            structure(row['essay'])
