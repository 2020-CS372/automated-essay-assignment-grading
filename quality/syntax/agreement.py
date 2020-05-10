import os
import sys
import nltk
from tqdm import tqdm
from nltk.tokenize import sent_tokenize, word_tokenize
from core.tree import TreeParser

#java_path = "C:/Program Files/Java/jdk1.8.0_251/bin/java.exe" # 이거 어떡하지?
#os.environ['JAVAHOME'] = java_path



def preprocessing(corpus):
    raw_articles = []
    for row in corpus:
        raw_articles.append(row['essay'])
    return raw_articles


def agreement(corpus):
    # Agreement in English
    # TODO : capture pairs to be matched(subject - main verb, det - noun)
    # using pos_tag to determine whether they're agreed or not
    
    wrong_cases = []
    singular_det = ['a', 'an', 'this', 'that', 'another', 'every', 'no']
    dontcare_det = ['some', 'any', 'all', 'each'] # 사실 don't care라기보단 문맥에 따라 다른거지만 일단은 임시로...
    PRP_3rd_person = ['he', 'she', 'it']
    articles = preprocessing(corpus)
    #parser = TreeParser()
    #parser.setup()
    #print("Setup done!")

    '''
    sentences = [
        'I love you',
        'He loves me',
        'She love him',
        'It likes me'
    ]
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
    for case in wrong_cases:
        print(case)
        print("")
    '''    


    
    
    
    
    #parser.stop_server()
    #print("Server stopped.")


    
    



if __name__ == "__main__":
    agreement()
