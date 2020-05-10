import nltk
import os
import re
import settings
import subprocess
from tqdm import tqdm
from nltk import sent_tokenize, RegexpTokenizer
from nltk.tree import ParentedTree
# from core.tree import TreeParser


def ambiguous(data, debug=False):
    for datum in tqdm(data):
        essay = datum['essay']
        sentences = sent_tokenize(essay)

        # not sastified but it works
        CORENLP_FOLDER_PATH = os.path.join(settings.BASE_DIR, 'data', 'corenlp')
        os.chdir(CORENLP_FOLDER_PATH)

        # sentences = [
        #     'I love you.',
        #     'Look at the dog with one eye.'
        # ]

        for sentence in sentences:
            
            # write sentences to datafile
            with open(
                os.path.join(CORENLP_FOLDER_PATH, '__test_sentence__.txt'),
                mode='w'
            ) as f:
                f.write(sentence)

            # getting output data
            terminal_output = subprocess.check_output(
                'java -mx500m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -printPCFGkBest 2 edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz __test_sentence__.txt',
                shell=True                
            )
            output = terminal_output.decode('utf-8')

            # extracting score
            tqdm.write(sentence)
            score = []
            score_strings = re.findall('# Parse (.*)\r\n', output)
            for idx, score_string in enumerate(score_strings):
                score.append(float(score_string.split('with score ')[1]))
                
                if idx == 0:
                    continue
                
                # tqdm.write(str(score))
                tqdm.write(str( score[idx] - score[idx - 1] ))