import csv
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

from core.tree import TreeParser

checked = []  # Array of (location, error_msg, peek sentence with part of prev_sentence)
parser = TreeParser()

"""
Captialization Rules [https://www.grammarly.com/blog/capitalization-rules/]
1. Capitalize the First Word of Sentence
2. Capitalize Names and Other Proper Nouns
3. Don’t Capitalize After a Colon (Usually)
4. Capitalize the First Word of a Quote (when the quote is a complete sentence)
5. Capitalize Days, Months, and Holidays, But Not Seasons
6. Capitalize Most Words in Titles
7. Capitalize Cities, Countries, Nationalities, and Languages
8. Capitalize Time Periods and Events (Sometimes)

9. Not on the rules
9-1. Pronoun 'I' should be capitalized
-------------------------------------------------------------------------------
Missing Capitalization
1 -> check_first_letter
4 -> check_quotations

Wrong Capitalization
3 -> check_wrong_capitalization
2,5,7,8,9-1 -> check_proper_noun

Others
6 -> Looks like there is no title in essays
"""


def check_first_letter(sentence, prev_sentence):
    return sentence[0] != sentence[0].upper() and (
        # TODO: dialogue form (ex. "~~~!" cries ~~.) need improvement
        prev_sentence == ""
        or prev_sentence[-1] not in ["'", '"']
    )

def check_quotations(essay):
    # TODO: Check if inside of quotation mark("~~~"/'~~~') is full sentence -> check_first_letter(sentence, "")
    return False


def check_proper_noun(sentence):
    # TODO: POS tag -> check capitalization of NNP & NNPS & PRP
    # Problem:
    # 1. word_tokenize breaks every words ex) 'New', 'York'
    # 2. default POS tagger classify NN to NNP if first is capitalized (...)
    return False


def check_wrong_capitalization(sentence):
    for char_idx in range(len(sentence)):
        character = sentence[char_idx]
        if character.isupper():
            # TODO: Do something with capitalized letter in wrong place
            # pass if char_idx==0 or in NNP or
            # Problem: Too specified and too many cases; we may classify correct one as error since we don't have it in case.
            pass
    return False


def capitalization(data):
    parser.setup()
    
    for datum in tqdm(data):
        essay_id, essay = datum["essay_id"], datum["essay"]
        sentences = sent_tokenize(essay)
        # print(sentences)
        sentence = ""
        for sent_idx in range(len(sentences)):
            prev_sentence = sentence
            sentence = sentences[sent_idx].strip()
            if check_first_letter(sentence, prev_sentence):
                checked.append(
                    (
                        f"Essay {essay_id} Sentence {sent_idx}",
                        "First letter of sentence must be capital letter.",
                        f"... {prev_sentence[-20:]} {sentence} ...",
                    )
                )
                
        if check_quotations(essay):
            checked.append(
                (
                    f"Essay {essay_id}",
                    "Full-sentence quotation starts with capital letter.",
                    f"... {prev_sentence[-20:]} {sentence} ...",
                )
            )

    print("Total", len(checked), "capitalization error found.")

    for c in checked:
        print(c)

    return checked
