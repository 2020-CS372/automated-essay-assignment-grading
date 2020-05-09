import csv
import os
import sys

import settings
from quality import QUALITY_DICT


QUALITY_DATA_PATH = os.path.join(settings.QUALITY_DATA_DIR, 'quality_data.csv')


def main():

    with open(QUALITY_DATA_PATH, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        quality_data_reader = list(reader)

    # TODO(Yohan): plagiarism data reader
    plagiarism_data_reader = None

    """
    plagiarism: python main.py (all/sample) (target) 여러개 가능
    quality: python main.py (all/sample) (semantics/syntax) (target) 여러개 가능
    """

    coverage = sys.argv[1]
    if len(sys.argv) == 3:
        if coverage == 'all':
            corpus = None
        elif coverage == 'sample':
            corpus = None
        target = sys.argv[2]

    elif len(sys.argv) == 4:
        if coverage == 'all':
            corpus = quality_data_reader
        elif coverage == 'sample':
            corpus = quality_data_reader[:10]

        quality_type = sys.argv[2]
        targets = sys.argv[3:]

        functions = []
        for target in targets:
            functions.append(QUALITY_DICT[target])

        for function in functions:
            function(corpus)


if __name__ == '__main__':
    main()
