import csv
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

checked = []  # Array of (location, error_msg, peek sentence with part of prev_sentence)

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
2,5,7,8,9-1 -> check_proper_noun
4 -> check_quote

Wrong Capitalization
3 -> check_wrong_capitalization

Others
6 -> Looks like there is no title in essays
"""


def quality_data():
    with open("data/quality_data/quality_data.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def check_first_letter(sentence, prev_sentence):
    return sentence[0] != sentence[0].upper() and (
        # TODO: dialogue form (ex. "~~~!" cries ~~.) need improvement
        prev_sentence == ""
        or prev_sentence[-1] not in ["'", '"']
    )


def check_proper_noun(sentence):
    # TODO: POS tag -> check capitalization of NNP & NNPS & PRP
    # Problem:
    # 1. word_tokenize breaks every words ex) 'New', 'York'
    # 2. default POS tagger classify NN to NNP if first is capitalized (...)
    return False


def check_quote(sentence):
    # TODO: Check if inside of quotation mark("~~~"/'~~~') is full sentence -> check_first_letter(sentence, "")
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


def capitalization(data=quality_data()):
    for datum in tqdm(data):
        essay_id, essay = datum["essay_id"], datum["essay"]
        sentences = sent_tokenize(essay)
        print(sentences)
        sentence = ""
        for sent_idx in range(len(sentences)):
            errorMsgs = []
            prev_sentence = sentence
            sentence = sentences[sent_idx].strip()
            if check_first_letter(sentence, prev_sentence):
                errorMsgs.append("First letter of sentence must be capital letter.")
            if check_proper_noun(sentence):
                errorMsgs.append("Proper noun must starts with capital letter.")
            if check_quote(sentence):
                errorMsgs.append("Full-sentence quotation starts with capital letter.")

            for msg in errorMsgs:
                checked.append(
                    (
                        f"Essay {essay_id} Sentence {sent_idx}",
                        msg,
                        f"... {prev_sentence[-20:]} {sentence} ...",
                    )
                )

    print("Total", len(checked), "capitalization error found.")
    return checked


if __name__ == "__main__":
    capitalization()
