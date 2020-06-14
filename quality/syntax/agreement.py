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


#java_path = "C:/Program Files/Java/jdk1.8.0_251/bin/java.exe" # 이거 어떡하지?
#os.environ['JAVAHOME'] = java_path



def preprocessing(corpus):
    raw_articles = []
    for row in corpus:
        raw_articles.append(row['essay'])
    return raw_articles


def get_answer(f_name):
    file_name = './' + f_name + '.xlsx'
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



def find_conj(dep_list, subj):
    for word in dep_list:
        if (word[1] == 'conj' and (word[0] == subj or word[2]== subj)):
            return True
    return False


def set_noun_num(dep_list, triple, postag_list):
    if (triple[2][1] in postag_list[2]): # 명사가 이미 복수형인 경우
        return 2
    
    elif (triple[2][1] in postag_list[3]): # 명사가 인칭 대명사인 경우, 'them'이나 their'도 포함시켜야 할까?
        if (triple[2][0].casefold() in ['i']):
            return 1
        elif (triple[2][0].casefold() in ['they', 'we', 'you']):
            return 2
        elif (triple[2][0].casefold() in ['us', 'them', 'her', 'him', 'me']):
            return 0
        else :
            return 3
    
    elif (triple[2][1] in postag_list[1]): # 명사가 단수형인 경우
        if (find_conj(dep_list, triple[2])):
            return 2
        else :
            return 3
    
    else :
        return 0


# have PP 현재완료 생각해 줘야 함
def set_verb_num(dep_list, triple, postag_list):
    for word in dep_list: # 찾은 동사가 agreement에 필요한 동사가 아닌경우
        if (word[1] == 'aux' and word[0] == triple[0]  and word[2][1] == 'MD'): # 조동사가 포함된 경우
            if (word[2][0].casefold() == 'does'): # does: 3인칭 단수
                return 5
            elif (word[2][0].casefold() == 'do'): # do: 그 외
                return 6 # 뭘로 return해야 되지
            else : # 다 똑같은 조동사 did, can, may ...
                return 7
        elif (word[1] == 'aux' and word[0] == triple[0] and word[2][1] in ['VBZ', 'VBD', 'VBP']): # 진행형
            if (word[2][0].casefold() in ['is', '\'s']):
                return 3
            elif (word[2][0].casefold() == 'was'):
                return 4
            elif (word[2][0].casefold() in ['are', 'were', '\'re']):
                return 2
        elif (word[1] == 'aux' and word[0] == triple[0] and word[2][0] in ['have', 'has', 'had', '\'ve']):
            if (word[2][0].casefold() in ['have', 've']):
                return 6
            elif (word[2][0].casefold() == 'has'):
                return 5
            else : # had
                return 7
    '''
    print("")
    print('normal')
    print("")
    print(triple)
    print(triple[0][1])
    print("")
    '''
    # 찾은 동사가 main verb인 경우
    if (triple[0][1] in ['VB', 'VBP']): # 동사원형 or 3인칭 단수가 아닌 동사
        return 6
    elif (triple[0][1] == 'VBZ'): # 3인칭 단수
        return 5
    elif (triple[0][1] == 'VBD'):
        return 7
    else :
        return 0


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


def agreement(corpus):
    # Agreement in English
    # TODO : capture pairs to be matched(subject - main verb, det - noun)
    # using pos_tag to determine whether they're agreed or not
    
    wrong_cases = []
    singular_det = ['a', 'an', 'this', 'that', 'another', 'every', 'no']
    dontcare_det = ['some', 'any', 'all', 'each'] # 사실 don't care라기보단 문맥에 따라 다른거지만 일단은 임시로...
    PRP_3rd_person = ['he', 'she', 'it']
    articles = preprocessing(corpus)
    parser = TreeParser()
    parser.setup()
    dep_parser = parser.dependency_parser
    
    
    #parser = TreeParser()
    #parser.setup()
    #print("Setup done!")

    '''
    tree = dep_parser.raw_parse('I\'ve reached top.')
    print(tree)

    
    temp = [[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in tree]
    for elem in temp[0]:
        print(elem)
        print()

    for elem in tree:
        print(elem.triples())
        print()
    '''

    # nsubj 기준으로 판단
    # 만약 aux가 있다면 aux를 기준으로 -> She doesn't like him. she 와 does를 비교 근데 이 경우는 do does 밖에 없을 듯. can may 등등 모두 해당사항 없음
    # 주어에 conj관계의 단어가 있는지 확인 -> He and I like her. like의 주어로는 He 만 감지됨.
    # 워낙 데이터가 개판이기 때문에 이를 감안해서 정상적인 문장이 들어왔을때 제대로 작동할 수 있도록 만들어 두고 채점기준에 대해서는 추후 다시 생각해 봐야 할 듯.
    # I'm eating hamburger 같은 문장에서 I'm 을 제대로 인식하지 못 하는 듯.
    # 근데 또 I'm riding a bike는 잘 함.
    # 동명사를 주어로 가지는 문장을 제대로 파악하지 못 하는 듯 함
    # 정확히는 목적어를 가지는 동사가 동명사의 형태로 주어에 위치하면 주어-동사 매칭을 재대로 성공시키지 못함
    # Eating gives me energy. -> 잘 함
    # Eating a sandwich gives me energy. -> 잘 함
    # Eating sandwiches gives me energy. -> 못 함. 아마도 det가 뭔가 정보를 더 주는 듯
    # 
    # 1. (A nsubj B) -> A: verb, B: noun 정상
    # 2. (A nsubj B) -> A: noun, B: noun 비정상 -> 주어를 잘 캐치했는데 동사를 제대로 캐치 못한경우와 아예 쌩판 이상한 단어들을 조합하는 경우 모두 포함됨
    #
    # 점수는 문장 단위로 내면 너무 점수가 박살날거 같으므로 주어-동사 쌍 단위로 계산
    # 어디가 틀렸는지 보여줄 필요 없이 그냥 점수만 매기자.
    # nsubj:pass도 따로 처리해줘야 함
    # noun
    # 0: nothing found -> 연구가 더 필요함
    # 1: 1인칭 단수
    # 2: 2인칭 + 복수
    # 3: 3인칭 단수
    # 4: don't care
    #
    # verb
    # 0: nothing found -> 연구가 더 필요함
    # 1: be 동사 1인칭 - am, 'm
    # 2: be 동사 2인칭 + 복수 - are, were, 're
    # 3: be 동사 3인칭 단수 - is
    # 4: be 동사 1인칭, 3인칭 단수 과거형 - was
    # 5: 3인칭 단수 - does, geos, gives
    # 6: 3인칭 단수가 아닌 나머지 - do, go, give
    # 7: don't care(do가 아닌 조동사 + 과거형) - did, can, may, ...
    #
    #





    #'''
    
    noun = ['NN', 'NNS', 'NNP', 'NNPS', 'PRP'] #0
    noun_singular = ['NN', 'NNP'] #1
    noun_plural = ['NNS', 'NNPS'] #2
    noun_personal = ['PRP'] #3

    verb = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] #4
    verb_1 = ['VB', 'VBD', 'VBP'] # 5   Verbs which can be used as main verb directly
    verb_2 = [''] #6

    postag_list = [noun, noun_singular, noun_plural, noun_personal, verb, verb_1, verb_2]
    
    correct = 0
    wrong = 0
    cnt = 1
    for article in articles[:10]:
        sentences = sent_tokenize(article)
        file_name = 'p' + str(cnt)
        ###answer = get_answer(file_name)
        true_positive = 0
        false_positive = 0
        false_negative = 0
        wrong_example = []

        # F-score도 문장마다 관리하자

        for sentence in sentences:
            ###answer_for_sentence = answer[sentences.index(sentence)]
            correct_relation = []
            wrong_relation = []
            #print(sentence)
            verb_num = 0
            noun_num = 0
            subj_verb = []
            tree = dep_parser.raw_parse(sentence)
            dep_list = [[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in tree]
            
            for dependency in dep_list[0]:              
                if dependency[1] == 'nsubj': # or 'nsubj:pass' for passive form
                    subj_verb.append(dependency)
            #print(dep_list)
                
            for triple in subj_verb:
                #print('in')
                #print(triple)
                if (triple[0][1] in verb and triple[2][1] in noun):
                    noun_num = set_noun_num(dep_list, triple, postag_list)
                    verb_num = set_verb_num(dep_list, triple, postag_list)
                    #print('noun_num : ' + str(noun_num))
                    #print('verb_num : ' + str(verb_num))
                    if (noun_num != 0 and  verb_num != 0): # noun and verb are properly identified.
                        if (verb_num == 7): # 동사가 don't care
                            correct_relation.append((triple[0][0], triple[2][0]))
                            correct += 1
                        elif (verb_num in [3, 5] and noun_num == 3): # 3인칭 단수
                            correct_relation.append((triple[0][0], triple[2][0]))
                            correct += 1
                        elif (verb_num == 1 and noun_num == 1): # 1인칭 단수
                            correct_relation.append((triple[0][0], triple[2][0]))
                            correct += 1
                        elif (verb_num == 4 and noun_num in [1, 3]): # edge case: was
                            correct_relation.append((triple[0][0], triple[2][0]))
                            correct += 1
                        elif (verb_num == 2 and noun_num == 2): # 2인칭 or 복수
                            correct_relation.append((triple[0][0], triple[2][0]))
                            correct += 1
                        elif (verb_num == 6 and noun_num != 3): # 3인칭이 아닌 일반 동사
                            correct_relation.append((triple[0][0], triple[2][0]))
                            correct += 1
                        else :
                            wrong_relation.append((triple[0][0], triple[2][0]))
                            wrong += 1
                            wrong_example.append([sentence, triple])

                    
                elif (triple[0][1] in noun and triple[2][1] in noun):
                    pass
                else :
                    pass
            ###print("")
            ###print(answer_for_sentence)
            ###print(correct_relation)
            ###print(wrong_relation)
            ###print("")
            ###tp, fp, fn = calculate_result(answer_for_sentence, correct_relation, wrong_relation)
            ###true_positive += tp
            ###false_positive += fp
            ###false_negative += fn

            
            #print(subj_verb)
            #print(correct_relation)
            #print(wrong_relation)
        cnt += 1
        
        # print(true_positive)
        # print(false_positive)
        # print(false_negative)
        # precision = true_positive/(true_positive + false_positive)
        # recall = true_positive/(true_positive + false_negative)
        # F_score = 2*precision*recall/(precision + recall)
        score = correct/(correct + wrong)
        # print('F_score : ' + str(F_score))
        print('score : ' + str(score))
        
        for elem in wrong_example:
            print(elem)
            print("")
    #'''
    '''
    sentences = [
        'I love you',
        'He loves me',
        'She love him',
        'It likes me'
    ]
    '''
    '''
    for article in articles:
    #article = articles[0]
        sentences = sent_tokenize(article)
        for sentence in sentences:
            words = word_tokenize(sentence)
            tagged_words = nltk.pos_tag(words)
            
            for i in range(len(tagged_words) - 1):
                # det - noun. det 'the' doesn't give any information about number of following word
                if (tagged_words[i][1] == 'DT' and tagged_words[i][0].lower() != 'the'): 

                    # detect plural det + singular noun
                    if (tagged_words[i+1][1] == 'NN' and tagged_words[i][0].lower() not in singular_det + dontcare_det):
                        wrong_cases.append((sentence, tagged_words[i][0], tagged_words[i+1][0], 'determinant is singular while noun is plural'))
                    
                    # detect singular det + plural noun
                    elif (tagged_words[i+1][1] == 'NNS' and tagged_words[i][0].lower() in singular_det):
                        wrong_cases.append((sentence, tagged_words[i][0], tagged_words[i+1][0], 'determinant is plural while noun is singular'))
                    
                    # 뒤에 바로 형용사가 명사가 나오지 않고 수식하는 단어가 추가되어 있는 경우 ex) a good man
                    else : 
                        j = i
                        while (tagged_words[j][1] == 'NN' or tagged_words[j][1] == 'NNS'):
                            j += 1
                        
                        # detect plural det + singular noun
                        if (tagged_words[j][1] == 'NN' and tagged_words[i][0].lower() not in singular_det + dontcare_det):
                            wrong_cases.append((sentence, tagged_words[i][0], tagged_words[j][0], 'determinant is singular while noun is plural'))
                        
                        # detect singular det + plural noun
                        elif (tagged_words[j][1] == 'NNS' and tagged_words[i][0].lower() in singular_det):
                            wrong_cases.append((sentence, tagged_words[i][0], tagged_words[j][0], 'determinant is plural while noun is singular'))
                       
                # simple subject - verb. Only bigram noun - VB or noun VBZ cases are detected.
                elif (tagged_words[i][1] == 'VB' or tagged_words[i][1] == 'VBZ'): # simple suject - verb
                    # questioning sentence
                    if (i == 0):
                        if (tagged_words[i][1] == 'VBZ'):
                            if (tagged_words[i+1][1] in ['NNS', 'NNPS']):
                                wrong_cases.append((sentence, tagged_words[i][0], tagged_words[i+1][0], 'verb is singular while noun is plural'))
                            elif (tagged_words[i+1][1] == 'PRP' and tagged_words[i][0].lower() not in PRP_3rd_person):
                                wrong_cases.append((sentence, tagged_words[i][0], tagged_words[i+1][0], 'verb is 3rd personal while noun is not'))

                        elif (tagged_words[i][1] == 'VB'):
                            if (tagged_words[i+1][1] == 'PRP' and tagged_words[i][0].lower() in PRP_3rd_person):
                                wrong_cases.append((sentence, tagged_words[i][0], tagged_words[i+1][0], 'verb is not 3rd personal while noun is'))
                    else :
                        if (tagged_words[i][1] == 'VBZ'):
                            if (tagged_words[i-1][1] in ['NNS', 'NNPS']):
                                wrong_cases.append((sentence, tagged_words[i-1][0], tagged_words[i][0], 'verb is singular while noun is plural'))
                            elif (tagged_words[i-1][1] == 'PRP' and tagged_words[i-1][0].lower() not in PRP_3rd_person):
                                wrong_cases.append((sentence, tagged_words[i-1][0], tagged_words[i][0], 'verb is 3rd personal while noun is not'))

                        elif (tagged_words[i][1] == 'VB'):
                            if (tagged_words[i-1][1] == 'PRP' and tagged_words[i][0].lower() in PRP_3rd_person):
                                wrong_cases.append((sentence, tagged_words[i-1][0], tagged_words[i][0], 'verb is not 3rd personal while noun is'))
    '''

    '''
    for case in wrong_cases:
        print(case)
        print("")
    '''    
    
    
    parser.free()
if __name__ == "__main__":
    agreement()