from core.tree import TreeParser
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.util import ngrams
from tqdm.auto import tqdm

def plagiarism(data, test_module = False):
    test_corpus, (source_corpus, suspicious_corpus) = data

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

    def predict(suspicious_corpus, source_corpus, train = False):
        results = {}

        for i, suspicious in enumerate(tqdm(suspicious_corpus)):
            suspicious_feature = generate_feature(suspicious['content'])
            word_suspicious, trigram_suspicious, structure_suspicious = suspicious_feature

            for j, source in enumerate(source_corpus):
                word_source, trigram_source, structure_source = source_features[j]

                # Jaccard Distance of words
                word_index = jaccard_distance(word_suspicious, word_source)

                # Jaccard Distance of trigrams
                trigram_index = jaccard_distance(trigram_suspicious, trigram_source)

                # Jaccard Distance of structures
                structure_index = jaccard_distance(structure_suspicious, structure_source)

                # Portion of LCS
                lcs_index = lcs(source['content'], suspicious['content'])[1]

                indexes = (word_index, trigram_index, structure_index, lcs_index)
                result = {
                    'indexes': indexes
                }

                if train:
                    result['is_plagiarism'] = source['name'] == suspicious['name']

                results[i, j] = result

        return results

    def train_normalization():
        results = predict(suspicious_corpus[:10], source_corpus[:10], True)
        nonplagiarism_values = [0, 0, 0, 0]
        nonplagiarism_count = 0

        for i in range(min(10, len(suspicious_corpus))):
            for j in range(min(10, len(suspicious_corpus))):
                if results[i, j]['is_plagiarism']:
                    continue

                for index_id, index_value in enumerate(results[i, j]['indexes']):
                    nonplagiarism_values[index_id] += index_value
                    nonplagiarism_count += 1

        nonplagiarism_mean = [x / nonplagiarism_count for x in nonplagiarism_values]

        plagiarism_variances = [0, 0, 0, 0]
        plagiarism_count = 0

        for i in range(min(10, len(suspicious_corpus))):
            for j in range(min(10, len(suspicious_corpus))):
                if not results[i, j]['is_plagiarism']:
                    continue

                for index_id, index_value in enumerate(results[i, j]['indexes']):
                    plagiarism_variances[index_id] += (index_value - nonplagiarism_mean[index_id]) ** 2
                    plagiarism_count += 1

        plagiarism_std = [(x / plagiarism_count) ** (1 / 2) for x in plagiarism_variances]

        return nonplagiarism_mean, plagiarism_std


    source_features = []
    print("[Plagiarism] Extracting features of sources")
    for source in tqdm(source_corpus):
        source_features.append(generate_feature(source['content']))


    print("[Plagiarism] Training Normalization")
    mean, std = train_normalization()


    print("[Plagiarism] Diffing essays")
    pred_results = predict(test_corpus, source_corpus, True)
    true_positive = 0
    false_positive = 0
    false_negative = 0
    detection = 0
    data_true = []
    data_false = []

    for i in range(len(test_corpus)):
        max_index = 0
        max_indexes = (0, 0, 0, 0)
        max_suspicious = 0
        max_iscorrect = False

        for j in range(len(source_corpus)):
            indexes = pred_results[i, j]['indexes']
            average = sum([(x - mean[i]) / std[i] for i, x in enumerate(indexes)])

            if pred_results[i, j]['is_plagiarism']:
                data_true.append(average)

            else:
                data_false.append(average)

            if average > max_index:
                max_index = average
                max_suspicious = j
                max_indexes = indexes
                max_iscorrect = pred_results[i, j]['is_plagiarism']

        if max_index > 1.2:
            print("[Plagiarism] Essay #%d with Source#%d, with Index %.4f" % (i, max_suspicious, max_index))

            if test_module:
                print(
                    (
                        "Word Index: %.4f, Structure Index: %.4f, Subsequence Index: %.4f, " +
                        "Trigram Index: %.4f, Correct: %s"
                    ) % (*max_indexes, str(max_iscorrect))
                )

            detection += 1

            if max_iscorrect:
                true_positive += 1

            else:
                false_positive += 1

        else:
            false_negative += 1

    if test_module:
        precision = true_positive / (true_positive + false_positive)
        recall = true_positive / (true_positive + false_negative)
        f_score = 2 * (1 / ((1 / precision) + (1 / recall)))
        print("Precision: %.4f, Recall: %.4f, F-Score: %.4f" % (precision, recall, f_score))
        print("TRUE" + ' '.join(["%.4f" % data for data in data_true]))
        print("FALSE" + ' '.join(["%.4f" % data for data in data_false]))

    parser.free()

    return detection
