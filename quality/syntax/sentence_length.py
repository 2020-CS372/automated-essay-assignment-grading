import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize.regexp import RegexpTokenizer

def preprocessing(corpus):
    raw_articles = []
    for row in corpus:
        raw_articles.append(row['essay'])
    return raw_articles


def sentence_length(corpus):
    too_long_sentences = []
    total_sentences = 0

    tokenizer = RegexpTokenizer("\s+", gaps=True)

    articles = preprocessing(corpus)
    for article in articles:
        sentences = sent_tokenize(article)
        total_sentences += len(sentences)
        for sentence in sentences:
            words = tokenizer.tokenize(sentence)
            if (len(words) > 25):
                too_long_sentences.append((sentence, len(words)))

    return (1 - len(too_long_sentences) / total_sentences) * 100


if __name__ == "__main__":
    sentence_length()
