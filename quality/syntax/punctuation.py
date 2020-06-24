from nltk import sent_tokenize, word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from tqdm.auto import tqdm

from core.tree import TreeParser


def sentence_to_subsentence(sentence):
    pass


def punctuation(data):
    parser = TreeParser()
    parser.setup()
    d = TreebankWordDetokenizer

    return_list = []
    for datum in data:
        essay = datum['essay']
        sentences = sent_tokenize(essay)

        wrong = 0
        wrong_sentences = []
        for sentence in sentences:
            # Endings (. ? !)
            endings = [i for i, x in enumerate(sentence) if x in ['.', '?', '!']]

            # Independent clause (;)
            semi_colons = [i for i, x in enumerate(sentence) if x == ';']

            if not endings:
                wrong += 1
                wrong_sentences.append(sentence)
                continue

            subsentence_indexes = [[0, endings[0]]]
            for i in range(1, len(endings)):
                subsentence_indexes.append([endings[i-1]+1, endings[i]])

            if semi_colons:
                for index in semi_colons:
                    for subsentence_index in subsentence_indexes:
                        start, end = subsentence_index
                        if start < index < end:
                            subsentence_indexes.remove(subsentence_index)
                            subsentence_indexes.append([start, index+1])
                            subsentence_indexes.append([index+2, end+1])

            subsentence_indexes.sort()

            subsentences = []
            for start, end in subsentence_indexes:
                subsentences.append(sentence[start:end+1])

            for subsentence in subsentences:
                forest = parser.parse(subsentence)
                ending = subsentence[-1]
                for tree in forest:
                    tree_string = str(tree)
                    if ('SQ' in tree_string) or ('SBARQ' in tree_string):
                        if not ending == '?':
                            wrong += 1
                            wrong_sentences.append(subsentence)
                            # print('question with no ?:', subsentence)
                            # print(tree.pretty_print())
                    else:
                        if ending == '?':
                            wrong += 1
                            wrong_sentences.append(subsentence)
                            # print('plain with ?:', subsentence)
                            # print(tree.pretty_print())

        essay_dict = {
            'essay_id': datum['essay_id'],
            'wrong_num': wrong,
            'wrong_sentences': wrong_sentences,
        }

        print(essay_dict)
        return_list.append(essay_dict)

    parser.free()
    return return_list

