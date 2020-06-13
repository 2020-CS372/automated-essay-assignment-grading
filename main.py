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

        for source in source_items:
            source = os.path.join(PLAGIARISM_SOURCE_PATH, source)
            with open(source, encoding = 'utf-8') as source_file:
                source_content = source_file.read()
                source_corpus.append(source_content)

        suspicious_corpus = []
        suspicious_items = os.listdir(PLAGIARISM_SUSPICIOUS_PATH)
        if nitems is not None:
            suspicious_items = suspicious_items[:nitems]

        for suspicious in suspicious_items:
            suspicious = os.path.join(PLAGIARISM_SUSPICIOUS_PATH, suspicious)
            with open(suspicious, encoding = 'utf-8') as suspicious_file:
                suspicious_content = suspicious_file.read()
                suspicious_corpus.append(suspicious_content)

        return source_corpus, suspicious_corpus

    all_functions = {}
    for key, plagiarism_fn in PLAGIARISM_DICT.items():
        all_functions[key] = {
            'type': 'plagiarism',
            'function': plagiarism_fn
        }

    for key, quality_fn in QUALITY_DICT.items():
        all_functions[key] = {
            'type': 'quality',
            'function': quality_fn
        }

    parser = argparse.ArgumentParser(description = 'Grade essay')
    parser.add_argument('--corenlp-url', dest = 'corenlp_url', required = False, default = None)
    parser.add_argument('coverage', choices = ('all', 'sample'))
    parser.add_argument('targets', nargs='*')

    args = parser.parse_args()
    functions = []

    if args.corenlp_url:
        settings.CORENLP_URL = args.corenlp_url

    for target in args.targets:
        if target not in all_functions:
            print("Unknown function: %s" % target)
            return

        functions.append(all_functions[target])

    if len(functions) == 0:
        functions = all_functions.values()

    for function_dict in functions:
        using_corpus = None

        if function_dict['type'] == 'plagiarism':
            using_corpus = plagiarism_data_reader

        elif function_dict['type'] == 'quality':
            using_corpus = quality_data_reader

        corpus = using_corpus(10 if args.coverage == 'sample' else None)
        function_dict['function'](corpus)


if __name__ == '__main__':
    main()
