from core.tree import TreeParser
from nltk import sent_tokenize, word_tokenize, pos_tag

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
    
    def traverse_inorder(tree):
        if isinstance(tree, str):
            return []
        
        inorder_list = []
        inorder_list.extend(traverse_inorder(tree[0]))
        inorder_list.append(tree.label())
        inorder_list.extend(traverse_inorder(tree[1]))
    
    def generate_structure_set(sents):
        sents_set = set()
        
        for sent in sents:
            forest = parser.parse(sent)
            if len(forest) == 0:
                continue
            
            tree = forest[0]
            inorder = tuple(traverse_inorder(tree))
            sents_set.add(inorder)
        
        return sents_set
    
    def lcs(sents1, sents2):
        words1 = []
        for sent in sent_tokenize(sents1):
            words1.extend(word_tokenize(sent))
        
        words2 = []
        for sent in sent_tokenize(sents2):
            words2.extend(word_tokenize(sent))
        
        table = [
            [ 0 for y in range(len(words1)) ] for x in range(len(words2))
        ]
        
        for y, word1 in enumerate(words1):
            for x, word2 in enumerate(words2):
                if word1 == word2:
                    table[y][x] = table[y - 1][x - 1] + 1
                    continue
                
                if x == 0 and y == 0:
                    continue
                
                if x == 0:
                    table[y][x] = table[y - 1][x]
                    continue
                
                if y == 0:
                    table[y][x] = table[y][x - 1]
                    continue
                
                table[y][x] = max(table[y - 1][x], table[y][x - 1])
        
        lcs_size = table[len(words1) - 1][len(words2) - 1]
        min_len = min(len(words1), len(words2))
        lcs_ratio = 0 if min_len == 0 else lcs_size / min_len
        
        return lcs_size, lcs_ratio
    
    for source, suspicious in data:
        # Jaccard Distance of words
        source_sents = sent_tokenize(source)
        source_set = generate_set(source_sents)
        
        suspicious_sents = sent_tokenize(suspicious)
        suspicious_set = generate_set(suspicious_sents)
        
        word_value = jaccard_distance(source_set, suspicious_set)
        
        # Jaccard Distance of structures
        source_structure_set = generate_structure_set(source)
        suspicious_structure_set = generate_structure_set(source)
        
        structure_value = jaccard_distance(
            source_structure_set, suspicious_structure_set
        )
        
        # Longest Common Subsequence
        lcs_value = lcs(source, suspicious)[1]
        
        print(word_value, structure_value, lcs_value)
    
    parser.free()

