import os
import sys
import nltk
from tqdm import tqdm
from nltk.tokenize import sent_tokenize, word_tokenize
from core.tree import TreeParser
from nltk.parse import CoreNLPParser, CoreNLPDependencyParser
from pprint import pprint
from nltk.tree import *
import pandas as pd

'''
Checking agreement between noun and verb in sentences.
Main noun(subject) and main verb should be matched in aspect of number.

EX) He goes to the shcool. (O)
    He go to the shchool. (X)
    I can do whatever I want. (O)
    I can does whatever I want. (X)
'''


# Extract essay data from raw data
def preprocessing(corpus):
    raw_articles = []
    for row in corpus:
        raw_articles.append(row['essay'])
    return raw_articles


# Extract self annotated answer for agreement from .xlsx file
def get_answer(f_name):
    file_name = './data/quality_data/agreement/' + f_name + '.xlsx'
    sheet = 'Sheet1'
    answer_array = []

    df = pd.read_excel(io = file_name, sheet_name = sheet)
    answer = df['annotation']
    
    for i in range(len(answer)):
        correct = []
        wrong = []
        if (answer[i] == '.'):
            break
        elif (type(answer[i]) == float):
            pass
        else :
            ano_list = answer[i].split(" | ")
            for ano in ano_list:
                ano_in_list = ano[1 : -1].split(", ")
                if (ano_in_list[-1] == '1'):
                    correct.append(tuple(ano_in_list[:2]))
                elif (ano_in_list[-1] == '2'):
                    wrong.append(tuple(ano_in_list[:2]))
        answer_array.append([correct, wrong])

    return answer_array


# True if there exist other subjects which are conjugated with given subject so that they must be treated as plural noun.
# False otherwise.
def find_conj(dep_list, subj):
    for word in dep_list:
        if (word[1] == 'conj' and (word[0] == subj or word[2]== subj)):
            return True
    return False


# noun
# 0: nothing found
# 1: 1st person singular noun
# 2: 2nd person + plural noun
# 3: 3rd person singular noun
# 4: don't care
def set_noun_num(dep_list, triple, postag_list):
    # Plural noun
    if (triple[2][1] in postag_list[2]):
        return 2
    
    # Personal noun
    elif (triple[2][1] in postag_list[3]):
        if (triple[2][0].casefold() in ['i']):
            return 1
        elif (triple[2][0].casefold() in ['they', 'we', 'you']):
            return 2
        elif (triple[2][0].casefold() in ['us', 'them', 'her', 'him', 'me']):
            return 0
        else :
            return 3
    
    # Singular noun or plural noun which is combination of more than one singular noun with conjugate such as 'and'.
    elif (triple[2][1] in postag_list[1]):
        if (find_conj(dep_list, triple[2])):
            return 2
        else :
            return 3
    
    else :  
        return 0


# verb
# 0: nothing found
# 1: 1st person singular be verb - am, 'm
# 2: 2nd person singular be verb + plural be verb - are, were, 're
# 3: 3rd person singular be verb - is
# 4: 1st, 3rd person singular past tense be verb - was
# 5: 3rd person singular verb - does, geos, gives
# 6: other than 3rd person verb - do, go, give
# 7: don't care(aux other than do or does + other past tense verb - did, can, may ...
def set_verb_num(dep_list, triple, postag_list):
    for word in dep_list: 
        # If found verb is not main verb -> need aux
        if (word[1] == 'aux' and word[0] == triple[0]  and word[2][1] == 'MD'):
            if (word[2][0].casefold() == 'does'):
                return 5
            elif (word[2][0].casefold() == 'do'):
                return 6
            else :
                return 7
        # present/past continuous
        elif (word[1] == 'aux' and word[0] == triple[0] and word[2][1] in ['VBZ', 'VBD', 'VBP']):
            if (word[2][0].casefold() in ['is', '\'s']):
                return 3
            elif (word[2][0].casefold() == 'was'):
                return 4
            elif (word[2][0].casefold() in ['are', 'were', '\'re']):
                return 2
        # present/past perfect
        elif (word[1] == 'aux' and word[0] == triple[0] and word[2][0] in ['have', 'has', 'had', '\'ve']):
            if (word[2][0].casefold() in ['have', 've']):
                return 6
            elif (word[2][0].casefold() == 'has'):
                return 5
            else :
                return 7

    # If found verb is main verb -> direct comparison
    if (triple[0][1] in ['VB', 'VBP']):
        return 6
    elif (triple[0][1] == 'VBZ'):
        return 5
    elif (triple[0][1] == 'VBD'):
        return 7
    else :
        return 0


# Calculate true_positive, false_positive, false_negative of given result. Used to calculate F-socre of model.
def calculate_result(answer_for_sentence, correct_relation, wrong_relation):
    correct_answer = answer_for_sentence[0]
    wrong_answer = answer_for_sentence[1]
    intersection_cnt = 0

    ca = len(correct_answer)
    wa = len(wrong_answer)
    cr = len(correct_relation)
    wr = len(wrong_relation)

    for elem in correct_relation:
        if (elem in correct_answer):
            intersection_cnt += 1
    for elem in wrong_relation:
        if (elem in wrong_answer):
            intersection_cnt += 1

    true_positive = intersection_cnt
    false_positive = cr + wr - intersection_cnt
    false_negative = ca + wa - intersection_cnt

    return true_positive, false_positive, false_negative


# Calculate F_score
def calculate_F_score(articles, dep_parser, postag_list):
    cnt = 1

    for article in articles[:1]:
        sentences = sent_tokenize(article)
        true_positive = 0
        false_positive = 0
        false_negative = 0
        
        # file should be svaed in /data/quality_data/agreement/ and file name should be p + essay number.
        file_name = 'p' + str(cnt)
        answer = get_answer(file_name)

        for sentence in sentences:
            answer_for_sentence = answer[sentences.index(sentence)]
            correct_relation = []
            wrong_relation = []
            verb_num = 0
            noun_num = 0
            subj_verb = []
            tree = dep_parser.raw_parse(sentence)
            dep_list = [[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in tree]         

            for dependency in dep_list[0]:              
                if dependency[1] == 'nsubj':
                    subj_verb.append(dependency)

            for triple in subj_verb:
                if (triple[0][1] in postag_list[4] and triple[2][1] in postag_list[0]):
                    noun_num = set_noun_num(dep_list[0], triple, postag_list)
                    verb_num = set_verb_num(dep_list[0], triple, postag_list)
                    if (noun_num != 0 and  verb_num != 0):
                        if (verb_num == 7):
                            correct_relation.append((triple[0][0], triple[2][0]))
                        elif (verb_num in [3, 5] and noun_num == 3):
                            correct_relation.append((triple[0][0], triple[2][0]))
                        elif (verb_num == 1 and noun_num == 1):
                            correct_relation.append((triple[0][0], triple[2][0]))
                        elif (verb_num == 4 and noun_num in [1, 3]):
                            correct_relation.append((triple[0][0], triple[2][0]))
                        elif (verb_num == 2 and noun_num == 2):
                            correct_relation.append((triple[0][0], triple[2][0]))
                        elif (verb_num == 6 and noun_num != 3):
                            correct_relation.append((triple[0][0], triple[2][0]))
                        else :
                            wrong_relation.append((triple[0][0], triple[2][0]))
            
            tp, fp, fn = calculate_result(answer_for_sentence, correct_relation, wrong_relation)
            true_positive += tp
            false_positive += fp
            false_negative += fn            
        
        cnt += 1
        
    precision = true_positive/(true_positive + false_positive)
    recall = true_positive/(true_positive + false_negative)
    F_score = 2*precision*recall/(precision + recall)

    return precision, recall, F_score
                            

# Main agreement function
def agreement(corpus):
    # Setup parser
    parser = TreeParser()
    parser.setup()
    dep_parser = parser.dependency_parser

    # Prepare data
    articles = preprocessing(corpus)
    
    # Set variables
    wrong_example = []
    all_results=[]
    
    noun = ['NN', 'NNS', 'NNP', 'NNPS', 'PRP'] #0
    noun_singular = ['NN', 'NNP'] #1
    noun_plural = ['NNS', 'NNPS'] #2
    noun_personal = ['PRP'] #3
    verb = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] #4
    verb_1 = ['VB', 'VBD', 'VBP'] # 5   Verbs which can be used as main verb directly
    verb_2 = [''] #6
    postag_list = [noun, noun_singular, noun_plural, noun_personal, verb, verb_1, verb_2]
  
    for article in tqdm(articles):
        sentences = sent_tokenize(article)
        correct = 0
        wrong = 0
     
        for sentence in sentences:
            verb_num = 0
            noun_num = 0
            subj_verb = []

            # Parse sentence and extract dependency between subject and verb
            tree = dep_parser.raw_parse(sentence)
            dep_list = [[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in tree]            
            
            for dependency in dep_list[0]:              
                if dependency[1] == 'nsubj': # or 'nsubj:pass' for passive form
                    subj_verb.append(dependency)

            # Search for wrong syntax
            for triple in subj_verb:
                if (triple[0][1] in verb and triple[2][1] in noun):
                    noun_num = set_noun_num(dep_list[0], triple, postag_list)
                    verb_num = set_verb_num(dep_list[0], triple, postag_list)
                    
                    if (noun_num != 0 and  verb_num != 0):
                        if (verb_num == 7): # verb is don't care
                            correct += 1
                        elif (verb_num in [3, 5] and noun_num == 3): # 3rd person singular 
                            correct += 1
                        elif (verb_num == 1 and noun_num == 1): # 1st person singular 인칭 단수
                            correct += 1
                        elif (verb_num == 4 and noun_num in [1, 3]): # edge case : was
                            correct += 1
                        elif (verb_num == 2 and noun_num == 2): # 2nd person or plural
                            correct += 1
                        elif (verb_num == 6 and noun_num != 3): # Otherwise
                            correct += 1
                        else :
                            wrong += 1
                            wrong_example.append([sentence, triple])
       
        score = correct/(correct + wrong)*100
        all_results.append(score)

    #precision, recall, F_score = calculate_F_score(articles, dep_parser, postag_list)
         
    parser.free()

    return score

if __name__ == "__main__":
    agreement()