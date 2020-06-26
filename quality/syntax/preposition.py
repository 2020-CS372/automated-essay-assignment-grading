import csv
import nltk
from core.tree import TreeParser
from nltk import sent_tokenize
from nltk.tree import ParentedTree
from tqdm import tqdm


"""
Preposition Rules [https://www.englishclub.com/grammar/prepositions-rules.htm]:

1. A preposition must have an object
2. A preposition usually comes before an object
3. A pronoun following a preposition should be in object form
4. A preposition is followed by a noun. It is NEVER followed by a verb.

IMPORTANT NODE TAGS:
    IN: Preposition or Subordinating conjunctions
    PP: <IN> <NP> chunk prepositions followed by NP

We have to check:
    - General (positions)
        1. PP with one child (which is IN)
        2. Duplicated/Lonely INs (or maybe not...)
"""


def traverse_tree(tree, nodes):
    # getting leaf nodes only
    for subtree in tree:
        if type(subtree) == nltk.tree.ParentedTree:
            traverse_tree(subtree, nodes)
        else:
            # print('appending... ', tree.flatten())
            # nodes.append((tree.label(), tree.leaves()))
            nodes.append(tree)


def error_string(message, sentence, word):
    return str(message) + ' for word \'' + str(word) + '\'' + ' in sentence \'' + str(sentence) + '\''


def preposition(data):
    # setup TreeParser
    parser = TreeParser()
    parser.setup()

    total_score = []

    # iterate all essay inputs
    for essay_data in data:
        tqdm_idx = 0

        # tokenize essay sentences
        essay = essay_data['essay']
        sentences = sent_tokenize(essay)

        # iterate for all sentences
        for sentence in tqdm(sentences):
            """
            Preprocessing sentence
            
            1. Parse and generate tree for one sentence in essay
            2. Convert tree to nltk ParentedTree
            3. Extract nodes in ParentedTree
            4. Find preposition nodes
            """
            in_nodes_count = 0
            res_list = []

            # parse sentence
            res = parser.parse(sentence)
            _dep_res = parser.dependency_parse(sentence)
            dep_res = _dep_res.__next__()

            for tree in res:
                # Convert nltk tree to nltk ParentedTree
                parented_tree = ParentedTree.convert(tree)

                # Getting nodes in tree
                nodes = []
                traverse_tree(parented_tree, nodes)

                # finding IN leaf nodes
                in_nodes = []
                node_idx = 0    # starts with 0, because there's ROOT node
                for node in nodes:
                    node_idx += 1
                    if node.label() == 'IN':
                        in_nodes.append((node_idx, node))

                # break for no PP sentence
                if len(in_nodes) <= 0:
                    # tqdm.write('There\'s no Preposition word.')
                    break
                in_nodes_count += len(in_nodes)

                """
                Testing preposition nodes with rules below:

                1. Ignore lonely IN - tehy're not actually PP (like 'if')
                2. PP must have an object (NP)
                3. PP usually comes before an object (WIP)
                """
                # check rules
                for node_idx, node in in_nodes:
                    # get parent pp node
                    parent = node.parent()

                    # check if a parent node does exist
                    if parent == None:
                        res_list.append(error_string(
                            'No parent node',
                        sentence, node.leaves()[0]))
                        continue

                    # check lonely IN
                    if parent.label() != 'PP':
                        # print for debug, actually not an grammar error
                        # res_list.append(error_string(
                        #    'No PP node but IN',
                        # sentence, node.leaves()[0]))
                        continue

                    # check if a PP have an object with DependencyParser
                    obj_exists = False

                    # check if dependency result has an same PP(IN) node
                    if not dep_res.contains_address(node_idx):
                        raise RuntimeError(
                                'Node\'s tag not exists in DEP dict.')
                    else:
                        _dep_node = dep_res.get_by_address(node_idx)
                        if node.label() != _dep_node['tag']:
                            raise RuntimeError(
                                'Node\'s tag not matches with DEP\'s tag.')

                    # check if dependency node has an object
                    for _dep_idx in range(len(nodes)):
                        _dep_idx += 1   # +1 for ignore ROOT node
                        _dep_val = dep_res.get_by_address(_dep_idx)
                        if _dep_val['deps']:
                            for _deps_case in _dep_val['deps']['case']:
                                if _deps_case == node_idx:
                                    obj_exists = True

                    # if PP do not have an object
                    if obj_exists == False:
                        res_list.append(error_string(
                            'Cannot find an object',
                        sentence, node.leaves()[0]))

            # adding score
            tqdm_idx += 1
            score = (1 - (float(len(res_list)) / max(in_nodes_count, 1))) * 100
            tqdm.write('Sentence #' + str(tqdm_idx) + ' / ' +
                        sentence[:10] + '...' + ': Score ' + str(score))
            for res in res_list:
                tqdm.write('#' + str(tqdm_idx) + ': ' + str(res))

            total_score.append(score)

    # returning total score
    print('pp total score', total_score)
    return sum(total_score) / max(1, len(total_score))


if __name__ == '__main__':
    # for debug
    with open('data\\quality_data\\quality_data.csv', encoding='utf-8') as f:
        reader=csv.DictReader(f)
        preposition(list(reader))
