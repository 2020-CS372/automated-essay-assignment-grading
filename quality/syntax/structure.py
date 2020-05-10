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
            # tree.pretty_print()

            if not check_root_clause(tree):
                continue

            # This didn't work as I expected
            # if not check_root_sv(tree):
            #    continue

            # if not check_noun_verb_ratio(tree):
            #     continue

            if not check_verb_for_clause(tree):
                continue


def stringify_tree(subtree):
    if type(subtree) == str:
        return subtree

    content = []
    for next_subtree in subtree:
        content.append(stringify_tree(next_subtree))

    return ' '.join(content)


# Check if root clause is not fragment
def check_root_clause(tree):
    main_elem = tree[0]
    if main_elem.label() not in CLAUSES:
        print("No root-level clause: %s / %s" % (main_elem.label(), stringify_tree(tree)))
        return False

    return True


# Check if root clause contains one subject, one verb
def check_root_sv(tree):
    # Find clause which height is lowest between clauses which contains VP / verbs
    def find_main_clause(tree):
        if type(tree) == str:
            return None

        for subtree in tree:
            if subtree.label() == 'VP' or subtree.label() in VERBS:
                return tree

            if subtree.label() in CLAUSES:
                main_clause = find_main_clause(subtree)
                if main_clause is not None:
                    return main_clause

        return None

    main_clause = find_main_clause(main_elem)
    if main_clause is None:
        print("No root-level verbs: %s" % stringify_tree(tree))
        return False

    main_np_count = 0
    for elem in main_clause:
        if elem.label() == 'NP':
            main_np_count += 1

    if main_np_count == 0:
        print("No root-level subjects: %s" % stringify_tree(tree))
        return False

    return True


def check_verb_for_clause(subtree):
    if type(subtree) == str:
        return True

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
            return False

    for next_subtree in subtree:
        if not check_verb_for_clause(next_subtree):
            return False

    return True


def check_noun_verb_ratio(tree):
    def count_noun_verb(subtree, counter):
        for next_subtree in subtree:
            if type(next_subtree) == str:
                continue

            if next_subtree.label() == 'VP':
                counter['v'] += 1

            elif next_subtree.label() == 'NP':
                counter['n'] += 1

            else:
                count_noun_verb(next_subtree, counter)

    counter = {'v': 0, 'n': 0}
    count_noun_verb(tree, counter)

    return counter['v'] <= counter['n']
