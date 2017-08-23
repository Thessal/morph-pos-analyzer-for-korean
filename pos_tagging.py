import os, sys
import pickle
import re
from bs4 import BeautifulSoup
import numpy as np
from morph_analysis import *
from hangul_utils import split_syllables, join_jamos

def dump(data, name):
    filehandler = open(name, "wb")
    pickle.dump(data, filehandler)
    filehandler.close()
def load(name):
    filehandler = open(name, "rb")
    return pickle.load(filehandler)

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
		
########################################################		
### Load Resources needed for POS tagging
########################################################
prob_pTagcTag = load('resources/prob_pTagcTag')
prob_TagWord = load('resources/prob_TagWord')
freq_Tag = load('resources/freq_Tag')

########################################################		
### Convert format
########################################################
def orgin_morph_idx(morph_result, idx):
    new_morph_result = [[]] * len(morph_result)
    
    for i, case in enumerate(morph_result):
        str_idx = idx
        temp = []
        for entry in case:
            origin_morph_info_list = entry[4:] # ['XSN NounV 이/XSN', 'VV VERB-L1 일/VV', 'VV VERB-S1 잇/VV']
            #print(entry)
            if len(origin_morph_info_list) == 1: # '+'이 없는 경우.
                
                if len(entry[-1].split()[-1].split('+'))==1:
                    #print('*** 1 ***')
                    #print(entry[0])
                    len_syllables_fix = len(split_syllables(entry[0]))
                    #print(origin_morph_info_list)
                    #print(entry[0])
                    org_morph = origin_morph_info_list[0].split()[-1].split('/')[0]
                    temp.append([org_morph, str_idx, str_idx+len_syllables_fix-1])
                    str_idx += len_syllables_fix
                    #print('1, temp: ',temp)
                    
                    
                else:
                    #print('*** 2 ***')
                    # 보통 2개로 나눠진다. ['에선', 8, 12, 'FUN', 'J N-1-0 에서/JKB+는/JX']처럼...
                    len_syllables_fix = len(split_syllables(entry[0])) # length 고정
                    str_idx_fix = str_idx
                    
                    plus_entry_list = entry[-1].split()[-1].split('+')
                    #print(entry)
                    #print(plus_entry_list)
                    
                    for m, pair in enumerate(plus_entry_list):
                        temp_length = 1 # +1씩하고 마지막꺼를 len_syllables_fix 길이와 맞추자.
                        org_morph = pair.split('/')[0]

                        if m == len(plus_entry_list)-1:
                            temp.append([org_morph, str_idx, str_idx_fix+len_syllables_fix-1])
                            str_idx = str_idx_fix + len_syllables_fix
                        else:
                            temp.append([org_morph, str_idx, str_idx+temp_length])
                            str_idx += temp_length+1                            
                            
                    #print('2, temp: ',temp)
                            
            else: # ['XSN NounV 이/XSN', 'VV VERB-L1 일/VV']와 같이 2개 이상
                #print('*** 3 ***')
                for k, each_morph_info in enumerate(origin_morph_info_list):
                    org_morph = each_morph_info.split()[-1].split('/')[0]
                    if k==0:
                        len_syllables_fix = len(split_syllables(entry[0]))
                    temp.append([org_morph, str_idx, str_idx+len_syllables_fix-1])
                    if k==len(origin_morph_info_list)-1:
                        str_idx += len_syllables_fix
                        
                    #print('3, temp: ',temp)
            
        new_morph_result[i] = temp
        #print('case', i, ':', temp)
        #print('\n')
        #print('--------------------> ',new_morph_result)
    return new_morph_result

def check_equal(cur_entry, list):
    for entry in list:
        if cur_entry == entry: # pair 전체가 같으면!. 만약 index가 다르면 에외 (ex. ['에서', 4, 6] ['에서', 3, 6])
            return True
    return False

def original_morphems(morph_result):
    uniqueEntry_list = []
    #print('-------->', morph_result)
    
    for case in morph_result:
        for entry in case:
            #print(entry)
            if check_equal(entry, uniqueEntry_list) == False: # 중복 체크
                uniqueEntry_list.append(entry)   
                

    #sorted1 = sorted(uniqueEntry_list, key=lambda k: k[1])
    sorted2 = sorted(uniqueEntry_list, key=lambda k: k[2])
    return sorted2

def convert_to_origin_morph(morph_result):
    final_entry_list = []
    str_idx = 0
    space_idx = []
        
    final_entry_list.append(original_morphems(orgin_morph_idx(morph_result, str_idx)))
    str_idx = original_morphems(orgin_morph_idx(morph_result, str_idx))[-1][2]+1
        
    #return final_entry_list, space_idx
    return final_entry_list


########################################################		
### Prepare pos tagging
########################################################
def indexing_for_sent(morph_result, str_idx):
    
    ### 일종의 버그가 있다. 공통적으로 있는 엔트리 (ex. '에')에 중복으로 str_idx가 더해지는 현상
    ### 그래서 그냥 새로운 리스트를 만들어서 처리하였다. 처리하는 김에 뒤에 엔트리 정보는 삭제하였다.
    ### [[['업', 0, 2, 'ENT', 'XPN NounC 업/XPN', 'XSN NounC 업/XSN'], ['계', 3, 4, 'ENT', 'NNG NounV 계/NNG', 'XSN NounV 계/XSN'], ['에', 5, 6, 'FUN', 'J N-1-0 에/JKB']], [['업계', 0, 4, 'ENT', 'NNG NounV 업계/NNG'], ['에', 5, 6, 'FUN', 'J N-1-0 에/JKB']]]
    ### str_idx 6
    ### [[['업', 6, 8], ['계', 9, 10], ['에', 11, 12]], [['업계', 6, 10], ['에', 11, 12]]]

    temp_morph_result = []
    
    for i, case in enumerate(morph_result):
        temp_case = []
        #print('[indexing_for_sent]', case)
        
        for j, ent in enumerate(case):
            temp_ent = []
            #print('morph_result[i][j][1]:', morph_result[i][j][1])
            #print(ent)
            #print(morph_result[i][j])
            temp_ent = morph_result[i][j][0:3]
            temp_ent[1] += str_idx
            temp_ent[2] += str_idx
            
            temp_case.append(temp_ent)
            #morph_result[i][j][1] = morph_result[i][j][1] + str_idx
            #morph_result[i][j][2] = morph_result[i][j][2] + str_idx
        temp_morph_result.append(temp_case)
    return temp_morph_result
	
def prepare_for_viterbi(sent, morph): # sent를 입력으로 index를 처리하자. 기존 morph는 어절밖에 하지 못한다.
    final_result = []
    str_idx = 0
    space_idx = []
        
    for i, token in enumerate(sent.split()):
        #print(token)
        morph_result = morph.extract(token)
        #print(morph_result)
        #print(len(morph_result))
        assert(len(morph_result)!=0) # 엔트리/기능어 사전에 해당 단어가 없을 경우.
        
        morph_result = convert_to_origin_morph(morph_result)
        #print('***   ',morph_result)
        #print('\n')
        #print('convert to origin !!!')
        
        #assert(len(morph_result)==0)
        #print(len(morph.extract(token)))
        #print('[morph.extract(token)]', morph.extract(token))

        reindexed_morph_result = indexing_for_sent(morph_result, str_idx)
        #print('str_idx', str_idx)
        #print(reindexed_morph_result)
        # 하나씩 넣기
        for case in reindexed_morph_result:
            for ent in case:
                if ent not in final_result: # 중복없이 넣기
                    final_result.append(ent)

        str_idx = reindexed_morph_result[0][-1][2] + 1
        space_idx.append(str_idx) # 어절마다 시작점이 어차피 space idx와 같다
        #print('\n\n')
        
    return final_result, space_idx	

	
########################################################		
### Main POS Tagging
########################################################		

def recursive_merging(collection, index_set, path, list_global_cases):
	temp_path = path[:]
	for index in index_set:
		path.append(index)
		index_set = [e for e in collection if int(e[1]) == index[2]+1] # first position
		if len(index_set) == 0: # the end point
			# save to global and then game over
			list_global_cases.append(path)
		else:
			# recursive keep going
			recursive_merging(collection, index_set, path, list_global_cases) # recursive function
		path = temp_path[:] # recursive돌아서 망가진 path 원래대로 복귀

# for viterbi
def extract_maxProb(tag_list, total_probState, i, j, prob_pTagcTag, output_probState):
    
    temp = [0] * len(tag_list)
    for k, _ in enumerate(tag_list):
    
        # 주의: underflow 방지를 위해 단순 multiplication이 아닌, log sum을 실시한다.
        # total_probState 변수는 이미 log화되어 있다.
        
        #print(total_probState[i-1][k], np.log(prob_pTagcTag[(tag_list[k], tag_list[j])]), np.log(output_probState[i][j]))
        temp[k] = total_probState[i-1][k] * prob_pTagcTag[(tag_list[k], tag_list[j])] * output_probState[i][j]  # index 주의
        
    max_prob = np.array(temp).max()
    argmax_idx = np.where(np.array(temp) == max_prob)
    
#     print(max_prob)
#     print(argmax_idx)
    
    index = argmax_idx[0][0] # (array([3], dtype=int64),) -> [0][0]해줘야 index 3가 추출된다.
    
#     print(index)
#     print(tag_list[index], index, '-', tag_list[j], j)
#     print('\n')
    return max_prob, index


		
def pos_tagging(sent):

	morph = Morph()
	result, space_idx = prepare_for_viterbi(sent, morph)
	
	
	final_collect_entry_anly = result
	len_target_word = result[-1][2]
	
	# sorting based on start index
	final_collect_entry_anly = sorted(final_collect_entry_anly, key = lambda x: int(x[1]))

	# 오류확인 1. 처음과 끝의 경계는 아래와 같이 체크하면 된다. (중간에 있는 오류는 다음단계에서 확인한다.)
	assert(final_collect_entry_anly[0][1] == 0) # 처음이 index 0으로 시작하지 않을 경우.
	assert(final_collect_entry_anly[-1][2] == len_target_word) # 마지막이 word길이만큼의 index가 아닐 경우.

	### merging / combining all cases using recursive function
	list_global_cases, path = [], []
	# filtering only index0 (Starting point to recursive function)
	index0_entry_anly_set = [ele for ele in final_collect_entry_anly if int(ele[1]) == 0] # first position
	# recursive merging
	recursive_merging(final_collect_entry_anly, index0_entry_anly_set, path, list_global_cases)


	# 오류확인 2. 처음부터 끝까지 이어지는 하나의 case도 없을 경우.
	fullpath_check = False
	for i in range(0, len(list_global_cases)):
		if list_global_cases[i][-1][2] == len_target_word:
			fullpath_check = True
	assert(fullpath_check == True) # 오류 난다면 사전 lookup 문제이다

	### Sequence가 0에서부터 len_target_word-1까지 이어지지 않으면 삭제한다.
	for i, seq in enumerate(list_global_cases):
		if seq[0][1] != 0 or seq[-1][2] != len_target_word:
			list_global_cases[i] = 'to-be-deleted'
	# remove elements, which has 'to-be-deleted' in the first position        
	list_global_cases = [elem for elem in list_global_cases if elem != 'to-be-deleted']	
	
	morph_result = list_global_cases

	##################################
	""" Viterbi Algorithm """
	##################################
	
	all_pos_cases = []
	all_jointprob_cases = []
	prob_case = [0] * len(morph_result)
	tag_list = list(freq_Tag.keys()) # 주의: tag_list와 freq_Tag.keys()의 배열 순서는 다르다.

	for case in morph_result: # 형태소 분석 조합 경우의 수
		output_probState = [[x for x in range(len(tag_list))] for y in range(len(case))]
		total_probState = [[x for x in range(len(tag_list))] for y in range(len(case))] # total probability on the state
		total_prev_state_idx = [[x for x in range(len(tag_list))] for y in range(len(case))] # optimal path (=[t-1] index) )
		pos_case = ['n'] * (len(case) + 1) # start token때문에 +1해준다
		joint_prob = 0
		
		
		###
		### Step 1: Assigning output probabliities
		### 일단 각 state에 대해 모든 출력확률을 구해놓는다
		for i, morph in enumerate(case): # 형태소 경우의 수
			cur_ent = morph[0]
			for j, tag in enumerate(tag_list): # POS Tag 경우의 수
				output_probState[i][j] = prob_TagWord[(tag, cur_ent)]
		
		
		###
		### Step 2: Storing only maximum probability to each state by multiplying transition probs
		for i, morph in enumerate(case): # 형태소 경우의 수
			for j, tag in enumerate(tag_list): # POS Tag 경우의 수
				#print('hi')
				if i==0: # prev time에 START밖에 없으므로 max확률 찾을필요없이 그냥 다 저장한다.
					pi_start_state = 1.0 # start state에 처음 있을 확률:100% 그냥 초기시작지점임.
					total_probState[i][j] = pi_start_state * prob_pTagcTag[('START', tag_list[j])] * output_probState[i][j]
					#total_probState[i][j] = output_probState[i][j]
					total_prev_state_idx[i][j] = tag_list.index('START') # 첫 번째 state는 항상 START와 연결
				else:
					total_probState[i][j], total_prev_state_idx[i][j] = extract_maxProb(tag_list, total_probState, i, j, prob_pTagcTag, output_probState)
					#print(total_probState[i][j], total_prev_state_idx[i][j])
		
		###
		### Step 3: Storing argmax index for connecting previous time
		temp = [0] * len(tag_list)
		last_idx = len(case)-1
		for j, _ in enumerate(tag_list):
			temp[j] = total_probState[last_idx][j] * prob_pTagcTag[(tag_list[j], 'END')]
			#temp[j] = total_probState[last_idx][j]
		
		# only for END tag
		max_prob = np.array(temp).max()
		end_idxState = np.where(np.array(temp) == np.array(temp).max())
		
		end_idxState = end_idxState[0][0] # for extracting only index
		#print(end_idxState, tag_list[end_idxState])
		#print(total_prev_state_idx)
		#print(total_prev_state_idx)
		
		###
		### Step 4: Doing Back-tracking
		tag_idx = -1
		for i, x in enumerate(reversed(pos_case)):
			last_idx = len(pos_case)-1
			idx = last_idx - i # reversed index
			
			if idx == last_idx: # last syllable
				pos_case[idx] = tag_list[end_idxState]
				joint_prob = max_prob
				tag_idx = end_idxState # for sending next time
			else:
				pos_case[idx] = tag_list[ total_prev_state_idx[idx][tag_idx] ]
				#joint_prob *= total_probState[idx][tag_idx]
				tag_idx = total_prev_state_idx[idx][tag_idx] # for sending next time
				#print(tag_idx)
				
			#print(pos_case)
				
		#print(pos_case)
		all_pos_cases.append(pos_case)
		all_jointprob_cases.append(joint_prob)
		#break
    
	
	### Viterbi End
	#####################
	
	### Extract The Answer
	all_jointprob_cases = np.array(all_jointprob_cases)
	indices = np.where(all_jointprob_cases == all_jointprob_cases.max())
	answer = np.where(all_jointprob_cases == all_jointprob_cases.max())
	answer_idx = answer[0][0] # 2개 이상이더라도 그냥 맨 처음에 있는 것을 argmax로 하자.
	

	best_morph_set = morph_result[answer_idx]
	best_pos_seq = all_pos_cases[answer_idx][1:] # 맨 앞 START를 제외하기 위해 [1:] 실시.
	
	final_str = ''
	for i, _ in enumerate(best_morph_set):
		final_str += best_morph_set[i][0]
		final_str += '/'
		final_str += best_pos_seq[i]
		if i != len(best_morph_set)-1:
			final_str += ' + '

	return final_str
	
	
	





