import csv

from nltk import word_tokenize, FreqDist, bigrams, PorterStemmer
from nltk.corpus import stopwords
from tqdm.auto import tqdm


def lexical_diversity(text):
    return len(set(text)) / len(text) * 100


# TODO(Jooyon): if duplicates is the keyword, do not deduct points. (Extracting keywords needed)
def duplicates(data):
    stop_words = list(stopwords.words('english'))
    stop_words.append('us')

    s = PorterStemmer()

    filtered_data = []
    for d in data:
        f_d = {
            'essay_id': d['essay_id'],
            'essay_set': d.get('essay_set'),
            'essay': d['essay'],
            'score': d.get('domain1_score'),
        }
        filtered_data.append(f_d)

    for d in tqdm(filtered_data):
        essay = d['essay']

        word_duplicates = []
        bigram_duplicates = []

        stem_words = []
        for word in word_tokenize(essay):
            if not word.isalpha():
                continue

            if word in stop_words:
                word = ''

            stem_words.append(s.stem(word))

        essay_bigrams = list(bigrams(stem_words))
        word_frequency = FreqDist(stem_words)
        bigram_frequency = FreqDist(essay_bigrams)

        word_frequency_list = list(word_frequency.items())
        word_frequency_list.sort(key=lambda element: element[1], reverse=True)

        bigram_frequency_list = list(bigram_frequency.items())
        bigram_frequency_list.sort(key=lambda element: element[1], reverse=True)

        for word, frequency in word_frequency_list:
            if not word:
                continue

            percentage = frequency / len(word_frequency_list)

            if frequency > 3 and percentage > 0.01:
                word_duplicates.append({
                    'word': word,
                    'frequency': frequency,
                    'percentage': percentage,
                })

        for (word1, word2), frequency in bigram_frequency_list:
            if not word1 or not word2:
                continue

            percentage = frequency / len(bigram_frequency_list)

            if frequency> 1 and percentage > 0.005:
                bigram_duplicates.append({
                    'bigram': (word1, word2),
                    'frequency': frequency,
                    'percentage': percentage,
                })

        d['lexical_diversity'] = lexical_diversity(word_tokenize(essay))
        d['word_duplicates'] = word_duplicates
        d['word_duplicates_num'] = len(word_duplicates)
        d['bigram_duplicates'] = bigram_duplicates
        d['bigram_duplicates_num'] = len(bigram_duplicates)

        tqdm.write(f"id:{d['essay_id']} - lexical_diversity: {round(d['lexical_diversity'], 2)}% - word_duplicates_num: {d['word_duplicates_num']} - bigram_duplicates_num: {d['bigram_duplicates_num']} - score: {d['score']}")

    return filtered_data
