import requests
import wikipediaapi
from nltk import word_tokenize
from nltk.corpus import wordnet, stopwords, words


DICTIONARY_WORDS = words.words()
WIKI = wikipediaapi.Wikipedia('en')


def typo(data):
    for datum in data:
        essay = datum['essay']
        words_ = word_tokenize(essay)
        words_ = [w for w in words_ if w.isalpha()]

        typos = []
        for word in words_:
            if word.lower() in stopwords.words('english'):
                continue

            synsets = wordnet.synsets(word.lower())
            if synsets:
                continue

            if word.lower() in DICTIONARY_WORDS:
                continue

            headers = {
                'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com',
                'x-rapidapi-key': '0615cad77amsh0e9589280e02861p12ae48jsnf926abb423f7',
            }
            url = f'https://wordsapiv1.p.rapidapi.com/words/{word.lower()}'
            response = requests.request('GET', url, headers=headers)

            if response.status_code == 404:
                # Checking newly coined words (e.g. cyberbullying)
                if not WIKI.page(word).exists():
                    typos.append(word)

        essay_dict = {
            'essay_id': datum['essay_id'],
            'typo_percentage': (len(typos) / len(words_)) * 100,
            'typos': typos,
        }

        print(essay_dict)
        return essay_dict
