import argparse
import csv
import os
import sys

import settings
from plagiarism import PLAGIARISM_DICT
from quality import QUALITY_DICT


QUALITY_DATA_PATH = os.path.join(settings.QUALITY_DATA_DIR, 'quality_data.csv')
PLAGIARISM_SOURCE_PATH = os.path.join(settings.PLAGIARISM_DATA_DIR, 'source')
PLAGIARISM_SUSPICIOUS_PATH = os.path.join(settings.PLAGIARISM_DATA_DIR, 'suspicious')

def main():
    with open(QUALITY_DATA_PATH, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        quality_data = list(reader)

    def quality_data_reader(nitems = None):
        if nitems is None:
            return quality_data

        return quality_data[:nitems]

    def plagiarism_data_reader(nitems = None):
        source_corpus = []
        source_items = os.listdir(PLAGIARISM_SOURCE_PATH)
        if nitems is not None:
            source_items = source_items[:nitems]

        for source_filename in source_items:
            source = os.path.join(PLAGIARISM_SOURCE_PATH, source_filename)
            with open(source, encoding = 'utf-8') as source_file:
                source_content = source_file.read()
                source_corpus.append({
                    'name': int(source_filename.split('_')[0]),
                    'content': source_content
                })

        suspicious_corpus = []
        suspicious_items = os.listdir(PLAGIARISM_SUSPICIOUS_PATH)
        if nitems is not None:
            suspicious_items = suspicious_items[:nitems]

        for suspicious_filename in suspicious_items:
            suspicious = os.path.join(PLAGIARISM_SUSPICIOUS_PATH, suspicious_filename)
            with open(suspicious, encoding = 'utf-8') as suspicious_file:
                suspicious_content = suspicious_file.read()
                suspicious_corpus.append({
                    'name': int(suspicious_filename.split('_')[0]),
                    'content': suspicious_content
                })

        return source_corpus, (source_corpus, suspicious_corpus)

    all_functions = {}
    for key, plagiarism_fn in PLAGIARISM_DICT.items():
        all_functions[key] = {
            'type': 'plagiarism',
            'function': plagiarism_fn,
            'name': key
        }

    for key, quality_fn in QUALITY_DICT.items():
        all_functions[key] = {
            'type': 'quality',
            'function': quality_fn,
            'name': key
        }

    parser = argparse.ArgumentParser(description = 'Grade essay')
    parser.add_argument('--corenlp-url', dest = 'corenlp_url', required = False, default = None)
    parser.add_argument('coverage', choices = ('all', 'sample', 'score'))
    parser.add_argument('--score-text', dest = 'text', required = False, default = None)
    parser.add_argument('targets', nargs='*')

    args = parser.parse_args()

    if args.corenlp_url:
        settings.CORENLP_URL = args.corenlp_url

    functions = []

    for target in args.targets:
        if target not in all_functions:
            print("Unknown function: %s" % target)
            return

        functions.append(all_functions[target])

    if len(functions) == 0:
        functions = all_functions.values()

    if args.coverage == 'score':
        if args.text:
            text = args.text

        else:
            r = open(settings.INPUT_FILE, mode='rt', encoding='utf-8')
            text = r.read()

        print(score(functions, {
            'quality': [{'essay_id': 'User input corpus', 'essay': text}],
            'plagiarism': ([{'name': 'score_corpus', 'content': text}], plagiarism_data_reader()[1])
        }))

        return

    for function_dict in functions:
        using_corpus = None

        if function_dict['type'] == 'plagiarism':
            using_corpus = plagiarism_data_reader

        elif function_dict['type'] == 'quality':
            using_corpus = quality_data_reader

        corpus = using_corpus(10 if args.coverage == 'sample' else None)
        function_dict['function'](corpus)


def score(functions, corpus):
    score_dict = {'plagiarism': {}, 'quality': {}}

    for func in functions:
        t, n = func['type'], func['name']
        try:
            score_dict[t][n] = func['function'](corpus[t])

        except Exception as ex:
            print(f'Error occurred in {n} : ', ex)

    print('\n\n--------------------------------')
    # return score_dict
    if score_dict['plagiarism']['plagiarism'] != 0:
        print('\n\nPlagiarism detected!!! No need for scoring!!!')
    else:
        default_score = 20
        score = default_score
        print('default_score:', default_score)

        # syntax
        print('capitalization:', max(10 - (score_dict['quality']['capitalization']) * 0.5, 0), '/10')
        score += max(10 - (score_dict['quality']['capitalization']) * 0.5, 0)
        print('preposition:', score_dict['quality']['preposition'] * 0.1, '/10')
        score += score_dict['quality']['preposition'] * 0.1
        print('punctuation:', max(10 - (score_dict['quality']['punctuation'][0]['wrong_num']) * 0.5, 0), '/10')
        score += max(10 - (score_dict['quality']['punctuation'][0]['wrong_num']) * 0.5, 0)
        print('structure:', score_dict['quality']['structure'] * 0.1, '/10')
        score += score_dict['quality']['structure'] * 0.1
        print('typo:', (100 - score_dict['quality']['typo']['typo_percentage']) * 0.1, '/10')
        score += (100 - score_dict['quality']['typo']['typo_percentage']) * 0.1
        print('agreement:', score_dict['quality']['agreement'] * 0.1, '/10')
        score += score_dict['quality']['agreement'] * 0.1
        print('sentence_length:', score_dict['quality']['sentence_length'] * 0.1, '/10')
        score += score_dict['quality']['sentence_length'] * 0.1

        # semantic
        print('ambiguous:', score_dict['quality']['ambiguous'] * 0.05, '/5')
        score += score_dict['quality']['ambiguous'] * 0.05
        temp = max(score_dict['quality']['duplicates'][0]['lexical_diversity'] * 0.05 - (score_dict['quality']['duplicates'][0]['bigram_duplicates_num']) * 0.25, 0)
        print('duplicates:', temp, '/5')
        score += temp

        print('\n\n======================')
        print(f'EssayCare total score: {score} / 100')



if __name__ == '__main__':
    main()
