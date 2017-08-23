from morph_analysis import *
import pickle
import os, sys
from bs4 import BeautifulSoup


def dump(data, name):
    filehandler = open(name,"wb")
    pickle.dump(data, filehandler)
    filehandler.close()


#################################
### Make morphological resources
#################################
	
trie = Trie()
trie_fun = Trie()
print(">>> Complete to load entTrie & funTrie")

trie = insert_dic_to_trie('ent', trie)
trie_fun = insert_dic_to_trie('fun', trie_fun)
print(">>> Complete to insert dic to entTrie & funTrie")

trie = insert_extdic_to_entTrie(trie)
print('>>> Complete to insert extdic to entTrie')


dump(trie, 'resources/ent_trie')
dump(trie_fun, 'resources/fun_trie')
print('>>> Complete to write entTrie & funTrie')



#######################
### Make POS resources
#######################

def find_leaf_node(tag):
    if tag.string!=None and tag.string!=' ' and len(list(tag.children))==1: # leaf node인지
        if '/' in list(tag.contents[0]) and len(tag.contents[0].split())!=1: # 형태소 분석된 정보인지
            return tag

def isPOStag(entry):
    # 세종 코퍼스 tagset은 총 45개이다. 하지만 여기서 코퍼스에서 존재하지 않는 'NF'와 'NV'는 제거하였다.
    # 나중에 'START'와 'END' tag를 추가하면 어차피 45개가 된다.
    tagSet = ['NNB', 'SH', 'VCN', 'EP', 'SF', 'NR', 'VCP', 'SW', 'XSN', 'JKV', 'XPN', 'MAJ', 'NP', 'MM', 'EF', 'SO', 'VX', 'EC', 'JKO', 'XR', 'NNG', 'JKG', 'JKC', 'SE', 'VA', 'IC', 'SN', 'SS', 'JKS', 'JC', 'JKQ', 'XSV', 'ETM', 'MAG', 'ETN', 'JKB', 'VV', 'SL', 'SP', 'JX', 'XSA', 'NA', 'NNP']
    if entry.split('/')[-1] in tagSet:
        return True
    else:
        return False
				
# Make resources from Sejoing Corpus
allTag_List = []
allWord_List = []
allTagWord_List = []
allpTagcTag_List = []

path = os.getcwd()+'\\saejongcorpus'
dirs = os.listdir(path)

for file in dirs:
    # read
    with open(path+'\\'+file, "rt", encoding='UTF8') as markup:
        soup = BeautifulSoup(markup.read(), "lxml")
    
    # working
    collection_leafNodes = soup.find_all(find_leaf_node)
    
    for leaf_node in collection_leafNodes: # <date>, <p> 와 같은 leaf node들을 traverse하겠다.

        #preTag = 'START'
        for i, entry in enumerate(leaf_node.contents[0].split()): # 그냥 공백으로 나눈 것들을 entry라고 하자.

            if isPOStag(entry) == True: # BSDO0276-00000009, 목젖으로, 목젖/NNG, +, 으로/JKB 에서 목젖/NNG과 으로/JKB만 걸러내겠다.
                
                ### 재료 준비
                tag = entry.split('/')[-1] # tag는 entry 마지막
                if len(entry.split('/')) == 3: # '/' 이것 때문에 예외처리하는 것이다. (ex //SP인 경우)
                    word = '/'
                else:
                    word = entry.split('/')[0] # word는 entry 첫번째
                
                # 의사__12/NNG -> '의사'로 처리해주기 위해...
                word = word.split('_')[0]
                
                # smoothing을 위해 모든 단어가 있는 voca 만듦
                allWord_List.append(word)
            
            
                #######################
                """ (tag)만 추출하자 """
                ####################### 
                allTag_List.append(tag)
                
                # START, END tag 만들어주기
                if i == 2:# i=0일 때는 BSAA0002-00000001이다. / i=1일 때는 좌우 / i=2일 때는 좌우__01/NNG
                    allTag_List.append('START') # START tag
                elif i == len(leaf_node.contents[0].split())-1:
                    allTag_List.append('END') # END tag            
                
                
                ############################
                """ (tag, word)를 추출하자 """
                ############################
                tagword_pair = (tag, word) 
                allTagWord_List.append(tagword_pair)
                
                
                ###################################
                """ (pre_tag, cur_tag)를 추출하자 """
                ###################################
                if i == 2: # 아마 여기가 제일 처음일 것이다.
                    pTagcTag_pair = ('START', tag)
                    allpTagcTag_List.append(pTagcTag_pair)
                    preTag = tag # 현재 tag를 할당
                elif i == len(leaf_node.contents[0].split())-1:
                    pTagcTag_pair = (tag, 'END')
                    allpTagcTag_List.append(pTagcTag_pair)
                else:
                    pTagcTag_pair = (preTag, tag)
                    allpTagcTag_List.append(pTagcTag_pair)

        #print('\n\n')

    #break

    
# ### DUMP
# dump(allTag_List, 'allTag_List')
# dump(allWord_List, 'allWord_List')
# dump(allTagWord_List, 'allTagWord_List')
# dump(allpTagcTag_List, 'allpTagcTag_List')


### Make Dictionary
# Word
freq_allWord = dict()
for i in allWord_List:
    freq_allWord[i] = freq_allWord.get(i, 0) + 1
# Tag
freq_allTag = dict()
for i in allTag_List:
    freq_allTag[i] = freq_allTag.get(i, 0) + 1
# Tag, Word
freq_allTagWord = dict()
for i in allTagWord_List:
    freq_allTagWord[i] = freq_allTagWord.get(i, 0) + 1
# pTag, cTag     
freq_allpTagcTag = dict()
for i in allpTagcTag_List:
    freq_allpTagcTag[i] = freq_allpTagcTag.get(i, 0) + 1

	

#### DUMP
#dump(freq_allTag, 'freq_allTag')
#dump(freq_allTagWord, 'freq_allTagWord')
#dump(freq_allWord, 'freq_allWord')
#dump(freq_allpTagcTag, 'freq_allpTagcTag')
#print('>>> Complete to write pair dictionaries')



freq_Tag = freq_allTag
freq_TagWord = freq_allTagWord # output probability를 구하기 위해
freq_Word = freq_allWord
freq_pTagcTag = freq_allpTagcTag # transition probability를 구하기 위해	



#########################
""" Smoothing """
#########################
def is_inDict(tag, word, dict):
    try:
        dict[(tag,word)]
    except(KeyError):
        return True # 사전에 없다
    return False	
	
### (Tag, Word) Smoothing...
# (Tag, Word)를 smoothing하기 위해 word voca를 구축.
for tag in freq_Tag:
    for word in freq_Word:
        if is_inDict(tag, word, freq_TagWord) == True: # 사전에 없는 경우
            freq_TagWord[(tag, word)] = 1 # smoothing으로 1 추가

# After smoothing...
# len(freq_allTagWord) = 9202185 <---------------- 너무 큰 것 아님........?????	

### (prevTag, curTag) Smoothing
for tag1 in freq_Tag:
    for tag2 in freq_Tag:
        if is_inDict(tag1, tag2, freq_pTagcTag) == True: # 사전에 없는 경우
            freq_pTagcTag[(tag1, tag2)] = 1 # smoothing으로 1 추가   

# Before smoothing...
# len(freq_allpTagcTag) = 1287
# After smoothing...
# len(freq_allpTagcTag) = 2025
	
	
#########################
""" Get Probabilities """
#########################
### p( Word | Tag )
prob_TagWord = freq_TagWord
for pos, _ in freq_Tag.items():
    # for each Tag
    temp = dict((k, v) for k, v in freq_TagWord.items() if k[0] == pos)
    total = sum(temp.values())
    for pair, value in temp.items():
        prob_TagWord[pair] = value / total
 
### printf 
#n = 0
#for key in prob_TagWord.items():
#    print(key)
#    n += 1
#    if n==10:
#        break	

### p( cTag | pTag )
prob_pTagcTag = freq_pTagcTag
for pTag, _ in freq_Tag.items():
    # for each previous Tag
    temp = dict((k, v) for k, v in freq_pTagcTag.items() if k[0] == pTag) # k[0]: previous tag
    total = sum(temp.values())
    for pair, value in temp.items():
        prob_pTagcTag[pair] = value / total  

### printf
#n = 0
#for key in prob_pTagcTag.items():
#    print(key)
#    n += 1
#    if n==10:
#        break		
	

	
	
#######################
### DUMP
#######################	 
dump(freq_Tag, 'resources/freq_Tag')
dump(freq_TagWord, 'resources/freq_TagWord')
dump(freq_Word, 'resources/freq_Word')
dump(freq_pTagcTag, 'resources/freq_pTagcTag')
print('>>> Complete to write freq dic')

dump(prob_pTagcTag, 'resources/prob_pTagcTag')
dump(prob_TagWord, 'resources/prob_TagWord')
print('>>> Complete to write prob dic')











