from core.tree import TreeParser
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.util import ngrams
from tqdm.auto import tqdm

def plagiarism(data):
    source_corpus, suspicious_corpus = data

    parser = TreeParser()
    parser.setup()

    def jaccard_distance(set1, set2):
        return len(set1 & set2) / len(set1 | set2)

    def generate_ngram_set(sents, ngram = 3):
        sents_set = set()

        for sent in sents:
            sents_set.update(ngrams([
                # "%s/%s" % pos_tag(word)
                word
                for word in word_tokenize(sent)
            ], ngram))

        return sents_set

    def traverse_preorder(tree):
        if isinstance(tree, str):
            return []

        preorder_list = [tree.label()]
        for leaf in tree:
            preorder_list.extend(traverse_preorder(leaf))

        return preorder_list

    def generate_structure_set(sents):
        sents_set = set()

        for sent in sents:
            if sent.strip() == '':
                continue

            try:
                tree = next(parser.parse(sent), None)
                if tree == None:
                    continue

                preorder = tuple(traverse_preorder(tree))
                sents_set.add(preorder)

            except:
                continue

        return sents_set

    def lcs(sents1, sents2):
        words1 = []
        for sent in sent_tokenize(sents1):
            words1.extend(word_tokenize(sent))

        words2 = []
        for sent in sent_tokenize(sents2):
            words2.extend(word_tokenize(sent))

        table = [
            [ 0 for y in range(len(words1) + 1) ] for x in range(len(words2) + 1)
        ]

        for y, word1 in enumerate(words1):
            for x, word2 in enumerate(words2):
                cur_y = y + 1
                cur_x = x + 1

                if word1 == word2:
                    table[cur_x][cur_y] = table[cur_x - 1][cur_y - 1] + 1
                    continue

                table[cur_x][cur_y] = max(table[cur_x - 1][cur_y], table[cur_x][cur_y - 1])

        lcs_size = table[len(words2)][len(words1)]
        min_len = min(len(words1), len(words2))
        lcs_ratio = 0 if min_len == 0 else lcs_size / min_len

        return lcs_size, lcs_ratio

    def generate_feature(corpus):
        sents = sent_tokenize(corpus)
        word_set = generate_ngram_set(sents, 1)
        trigram_set = generate_ngram_set(sents, 3)
        structure_set = generate_structure_set(sents)

        return (word_set, trigram_set, structure_set)

    source_features = []
    print("[Plagiarism] Extracting features of sources")
    for source in tqdm(source_corpus):
        source_features.append(generate_feature(source))

    print("[Plagiarism] Diffing essays")
    for i, suspicious in tqdm(enumerate(suspicious_corpus)):
        suspicious_feature = generate_feature(suspicious)
        word_suspicious, trigram_suspicious, structure_suspicious = suspicious_feature
        max_index = 0
        max_indexes = (0, 0, 0, 0)
        max_suspicious = 0

        for j, source in enumerate(source_corpus):
            word_source, trigram_source, structure_source = source_features[j]

            # Jaccard Distance of words
            word_index = jaccard_distance(word_source, word_suspicious)

            # Jaccard Distance of trigrams
            trigram_index = jaccard_distance(trigram_suspicious, trigram_source)

            # Jaccard Distance of structures
            structure_index = jaccard_distance(structure_suspicious, structure_source)

            # Portion of LCS
            lcs_index = lcs(source, suspicious)[1]

            indexes = (word_index, trigram_index, structure_index, lcs_index)
            average = sum(indexes) / 4

            if average > max_index:
                max_index = average
                max_suspicious = j
                max_indexes = indexes

        if max_suspicious > 0.125:
            tqdm.write("[Plagiarism] Essay #%d with Source#%d, with Index %.4f" % (i, max_suspicious, max_index))
            tqdm.write(
                "Word Index: %.4f, Structure Index: %.4f, Subsequence Index: %.4f, Trigram Index: %.4f" %
                max_indexes
            )

    parser.free()
