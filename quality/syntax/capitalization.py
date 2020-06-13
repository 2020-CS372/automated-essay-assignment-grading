import csv
from nltk import ne_chunk, pos_tag
from nltk.tree import Tree
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag.stanford import StanfordNERTagger
from tqdm import tqdm

import settings
from core.tree import TreeParser

parser = TreeParser()
ner_tagger = StanfordNERTagger(
    settings.STANFORD_NER_MODEL, settings.STANFORD_NER_JAR, encoding="utf-8"
)

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


def check_proper_noun(sentence, stanford=False):
    proper_noun_not_capitalized = []

    if not stanford:
        POS_tagged_sent = pos_tag(word_tokenize(sentence))

        parsed_tree = ne_chunk(POS_tagged_sent, binary=True)
        for subtree in parsed_tree.subtrees():
            if subtree.label() == "NE":
                NE = " ".join([leaf[0] for leaf in subtree.leaves()])
                NE = (
                    NE.strip()
                    .replace("( ", "(", NE.count("( "))
                    .replace(" )", ")", NE.count(" )"))
                    .replace(" .", ".", NE.count(" ."))
                    .replace(" ,", ",", NE.count(" ,"))
                )
                if NE[0] != NE[0].upper():
                    proper_noun_not_capitalized.append((NE, "NE"))
        for word, tag in POS_tagged_sent:
            if tag in ["NNP", "NNPS"] and word[0] != word[0].upper():
                proper_noun_not_capitalized.append((word, tag))

    else:
        checked = []
        parsed_tree = list(parser.parse(sentence))[0]
        leaves = parsed_tree.leaves()

        tagged_sent = ner_tagger.tag(leaves)
        prev_tag = "O"
        NEs = []
        NE = []
        for (idx, (word, tag)) in enumerate(tagged_sent):
            if prev_tag != tag:
                if len(NE) > 0 and prev_tag != "O":
                    NEs.append(NE)
                NE = []
            if tag != "O":
                NE.append(word)
                checked.append(idx)
            prev_tag = tag

        for ne in NEs:
            capitalized = True
            for word in ne:
                if word[0] != word[0].upper():
                    capitalized = False
            if not capitalized:
                proper_noun_not_capitalized.append((" ".join(ne), "NE"))

        for subtree in parsed_tree.subtrees():
            if type(subtree) == Tree:
                if subtree.label() in ["NNP", "NNPS"]:
                    words = subtree.leaves()
                    for word in words:
                        if word[0] != word[0].upper():
                            if leaves.index(word) not in checked:
                                proper_noun_not_capitalized.append(
                                    (word, subtree.label())
                                )

    return proper_noun_not_capitalized


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
    checked = []  # Array of (location, error_msg, peek sentence with part of prev_sentence)

    parser.setup()
    print(list(parser.parse("Parser setup")))
    print(ner_tagger.tag(word_tokenize("Stanford NER tagger setup")))

    for datum in tqdm(data, "Capitalization Checking"):
        essay_id, essay = datum["essay_id"], datum["essay"]
        sentences = sent_tokenize(essay)
        # print(sentences)
        sentence = ""
        for sent_idx in tqdm(range(len(sentences)), f"Essay {essay_id}"):
            prev_sentence = sentence
            sentence = sentences[sent_idx].strip()
            if check_first_letter(sentence, prev_sentence):
                checked.append(
                    (
                        f"Essay {essay_id} Sentence {sent_idx}",
                        "First letter of sentence must be capital letter.",
                        f"... {prev_sentence[-10:]} {sentence[10:]} ...",
                    )
                )

            prop_noun_result = check_proper_noun(sentence, stanford=True)
            if len(prop_noun_result) > 0:
                for prop_noun, explanation in prop_noun_result:
                    checked.append(
                        (
                            f"Essay {essay_id} Sentence {sent_idx}",
                            f"Proper noun '{prop_noun}({explanation})' in this sentence needs capitalization.",
                            f"... {sentence} ...",
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

        tqdm.write(f"Essay {essay_id} Total {len(checked)} tense error found.")

        with open('./quality/syntax/capitalization.log', 'a', encoding='utf-8') as file:
            for c in checked:
                file.write(str(c)+'\n')
        
        checked = []
    
    parser.free()

    return
