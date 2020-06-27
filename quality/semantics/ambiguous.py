import nltk
import os
import re
import settings
import subprocess
from tqdm import tqdm
from nltk import sent_tokenize, RegexpTokenizer
from nltk.tree import ParentedTree


def ambiguous(data, debug=False):
    """
    Finding ambiguity

    1. Extract PCFG trees (two high probability score tree) using LexicalizedParser
    2. Calculate the probability difference between first and second probabilty tree
    3. Calculate ambiguity
        3-1. If the value of (2) is over than high threshold,
                it is not ambiguous sentence. Score is 100.
        3-2. If the value of (2) is lower than low threshold,
                the sentence's structure is too bad for essay. Score is 0.
        3-3. If not (3-1) and (3-2),
                return the score calculated by dividing
                difference between high threshold and value of (2) with
                high threshold and normalize it to 100-max-score-based score.
    """

    threshold_high = 0.75
    threshold_low = 0.05

    total_score = []

    for datum in tqdm(data):
        essay = datum['essay']
        sentences = sent_tokenize(essay)

        # not sastified but it works
        CORENLP_FOLDER_PATH = os.path.join(
            settings.BASE_DIR, 'data', 'corenlp')
        os.chdir(CORENLP_FOLDER_PATH)

        for sentence in sentences:
            # write sentences to datafile
            with open(
                os.path.join(CORENLP_FOLDER_PATH, '__test_sentence__.txt'),
                mode='w'
            ) as f:
                f.write(sentence)

            # 1. extract PCFG tree by getting output data from LexicalizedParser
            terminal_output = subprocess.check_output(
                'java -mx500m -cp "*" edu.stanford.nlp.parser.lexparser.LexicalizedParser -printPCFGkBest 2 edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz __test_sentence__.txt',
                shell=True
            )
            output = terminal_output.decode('utf-8')

            # extracting tree score
            tqdm.write('\n' + sentence)
            score = []
            
            # parse PCFG tree probabilities
            score_strings = re.findall('# Parse (.*)', output)
            for idx, score_string in enumerate(score_strings):
                score.append(float(score_string.split('with score ')[1]))

                if idx == 0:
                    continue

                # 2. extract difference between probabilities
                difference = ((score[idx] - score[idx - 1]) * -1)

                # 3-1. if score is over thresholod
                if difference > threshold_high:
                    total_score.append(100)
                    tqdm.write('Good clarity: ' + str(difference * 100))
                    continue

                # 3-2. if sentence structure is too bad
                if difference < threshold_low:
                    tqdm.write('Sentence is too bad: ' + str(difference * 100))
                    total_score.append(0)
                    continue
                
                # 3-3. if score is in threshold range
                normal_score = difference / max(threshold_high, 0.01) * 100
                total_score.append(normal_score)
                tqdm.write('Clarity: ' + str(difference * 100))
                tqdm.write('Score: ' + str(normal_score))
                tqdm.write('\n')

    # return average score
    return sum(total_score) / max(1, len(total_score))