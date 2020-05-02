import csv
from nltk.tokenize import sent_tokenize
from tqdm import tqdm

checked = []  # Array of (location, error_msg, peek sentence with part of prev_sentence)


def quality_data():
    with open("data/quality_data/quality_data.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def check_first_letter(sentence, prev_sentence):
    return sentence[0] != sentence[0].upper() and (
        prev_sentence == "" or prev_sentence[-1] not in ["'", '"']
    )


def capitalization(data=quality_data()):
    for datum in tqdm(data):
        essay_id, essay = datum["essay_id"], datum["essay"]
        sentences = sent_tokenize(essay)
        sentence = ""
        for sent_idx in range(len(sentences)):
            errorMsgs = []
            prev_sentence = sentence
            sentence = sentences[sent_idx].strip()
            if check_first_letter(sentence, prev_sentence):
                errorMsgs.append("First letter of sentence must be capital letter.")

            for msg in errorMsgs:
                checked.append(
                    (
                        f"Essay {essay_id} Sentence {sent_idx}",
                        msg,
                        f"...{prev_sentence[-20:]} {sentence} ...",
                    )
                )

    print("Total", len(checked), "capitalization error found.")
    return checked


if __name__ == "__main__":
    capitalization()
