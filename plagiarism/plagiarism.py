from core.tree import TreeParser
from nltk import sent_tokenize, word_tokenize, pos_tag
from tqdm.auto import tqdm

def plagiarism(data):
    parser = TreeParser()
    parser.setup()

    def jaccard_distance(set1, set2):
        return len(set1 & set2) / len(set1 | set2)

    def generate_set(sents):
        sents_set = set()

        for sent in sents:
            sents_set.update([
                # "%s/%s" % pos_tag(word)
                word
                for word in word_tokenize(sent)
            ])

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

    for source, suspicious in tqdm(data):
        # Jaccard Distance of words
        source_sents = sent_tokenize(source)
        source_set = generate_set(source_sents)

        suspicious_sents = sent_tokenize(suspicious)
        suspicious_set = generate_set(suspicious_sents)

        word_value = jaccard_distance(source_set, suspicious_set)

        # Longest Common Subsequence
        lcs_value = lcs(source, suspicious)[1]

        # Jaccard Distance of structures
        source_structure_set = generate_structure_set(source_sents)
        suspicious_structure_set = generate_structure_set(suspicious_sents)

        structure_value = jaccard_distance(
            source_structure_set, suspicious_structure_set
        )

        tqdm.write(
            "Word Index: %.4f, Structure Index: %.4f, Subsequence Index: %.4f" %
            (word_value, structure_value, lcs_value)
        )

    parser.free()
