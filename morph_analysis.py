from hangul_utils import split_syllables, join_jamos
import xlrd
import pickle

######################
### make_resuourse.py
######################
# li_initial_phonemes = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# li_medial_phonemes = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
# li_final_phonemes = ['ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', 'null']
# sample_text = '가까웠지만'
# jamo = split_syllables(sample_text)
# print(jamo)
# restored_text = join_jamos(jamo)
# print(restored_text)

# 수정해야 되는 불규칙 정보. (예: VERB-REG1~3, ADJ-REG1~3)
# 원래대로라면, trie class에 modify함수가 있어서 수정해야함.
def infl_modify_REG(word, pos, inf):
    reg1_list = ['ㅑ','ㅒ','ㅖ','ㅘ','ㅛ','ㅙ','ㅚ','ㅝ','ㅠ','ㅡ','ㅢ','ㅣ']
    reg2_list = ['ㅗ','ㅜ']
    reg3_list = ['ㅏ','ㅓ','ㅕ','ㅐ','ㅔ','ㅞ']
    
    if inf == 'VERB-REG' or inf == 'ADJ-REG':
        word = split_syllables(word)
        list_word = list(word)
        
        if list_word[-1] in reg1_list:
            word = "".join(list_word)
            word = join_jamos(word)
            inf = inf + '1'
        elif list_word[-1] in reg2_list:
            word = "".join(list_word)
            word = join_jamos(word)
            inf = inf + '2'            
        elif list_word[-1] in reg3_list:
            word = "".join(list_word)
            word = join_jamos(word)
            inf = inf + '3'              
        else:
            word = "".join(list_word)
            word = join_jamos(word)            
            return word, pos, inf # -REG0이므로, 그냥 패스
        return word, pos, inf # 수정된 내용이 반영된 정보 return
    else:
        return word, pos, inf # -REG가 아니므로 (modify할 필요x), 그냥 패스

########################################
""" 효율적인 검색을 위한 trie자료구조 """
########################################
class Trie(list):
    
    def __init__(self):
        chs = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', 'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', 'ㄲ', 'ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ', 'ㅆ']
        self.extend([ [None, None] for a in range(len(chs)) ]) # 왼쪽 None: 현재 ch의 info저장, 오른쪽 None: 다음 ch와 연결되는 노드
        self.dic = {}
        for i, ch in enumerate(chs):
            self.dic[ch] = i # look up table for 한글
        
    def index(self,ch):
        return self.dic[ch]
    
    def insert(self, word, info_list):
        word = split_syllables(word)
        if(len(word)==1):
            self.set_info(word, info_list)
        else:
            f_word = word[0]
            word = word[1:]
            char_idx = self.index(f_word)
            
            # [1]인 이유: 다음 ch와 연결되는 노드는 오른쪽 None에 저장한다.
            if (self[char_idx][1] == None):
                self[char_idx][1] = Trie()
                self[char_idx][1].insert(word,info_list)
            else:
                self[char_idx][1].insert(word,info_list)
            
    def set_info(self, f_word, _info):
        # [0]인 이유: info를 저장할 땐 왼쪽 None에 저장한다.
        if self[self.index(f_word)][0] == None:
            self[self.index(f_word)][0] = [_info] # 1개라도 배열로 처리
        else: # 중복처리
            #print(self[self.index(f_word)][0])
            temp = []
            temp += self[self.index(f_word)][0]
            temp += [_info]
            self[self.index(f_word)][0] = temp[:]
    
    def search(self, trie_list, word):
        word = split_syllables(word)
        if(len(word)==1):
            return trie_list[self.index(word)][0] # info를 출력할 땐, 왼쪽 None을 출력한다.
        else:
            f_word = word[0]
            word = word[1:]
            char_idx = self.index(f_word) 
            return self.search(trie_list[char_idx][1], word) # Search를 찾아나설 땐, 오른쪽 None에 저장된 연결된 노드들을 따라 나선다.

def search(trie, word):
    try:
        if trie.search(trie, word) == None:
            return "No such word in Trie"
        else:
            return trie.search(trie, word)
    except(TypeError):
        return "No such word in Trie"
###############################################################################

def insert_dic_to_trie(ent_or_fun, trie_class):

	workbook = xlrd.open_workbook('assets/voca_set.xlsx')

	if ent_or_fun == 'fun': # 기능어 사전
		
		worksheet2 = workbook.sheet_by_name('기능어사전')
		num_rows = worksheet2.nrows #줄 수 가져오기
		num_cols = worksheet2.ncols #칸 수 가져오기

		# row_val = worksheet_name.row_values(row_index) #줄 값 가져오기(list형식)
		# cell_val = worksheet_name.cell_value(row_index,cell_index)

		for i in range(1, num_rows):
			word = worksheet2.cell_value(i, 0)
			pos = worksheet2.cell_value(i, 1)
			inf = worksheet2.cell_value(i, 2)
			anly = worksheet2.cell_value(i, 3)
			_info = pos+' '+inf+' '+anly
			decomposed_w = split_syllables(word)
			reversed_w = decomposed_w[::-1] # reverse하기 위해 decomposition 미리 실시
			trie_class.insert(reversed_w, _info) # 이미 decomposition되어 있지만 상관없음
		
	
	else: # 엔트리 사전
	
		worksheet1 = workbook.sheet_by_name('엔트리사전')
		num_rows = worksheet1.nrows #줄 수 가져오기
		num_cols = worksheet1.ncols #칸 수 가져오기

		# row_val = worksheet_name.row_values(row_index) #줄 값 가져오기(list형식)
		# cell_val = worksheet_name.cell_value(row_index,cell_index)

		for i in range(1, num_rows):
			word = worksheet1.cell_value(i, 0)
			pos = worksheet1.cell_value(i, 1)
			inf = worksheet1.cell_value(i, 2)
			word, pos, inf = infl_modify_REG(word, pos, inf)
			
			anly = word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie_class.insert(word, _info) # word는 insert함수에 의해 decomposition된다.

	return trie_class

##########################################################################################################

DEBUG = False
def LOG(s):
    if DEBUG:
        print(s)

def insert_extdic_to_entTrie(trie):

	workbook = xlrd.open_workbook('assets/voca_set.xlsx') 
	worksheet1 = workbook.sheet_by_name('엔트리사전')
	num_rows = worksheet1.nrows #줄 수 가져오기
	num_cols = worksheet1.ncols #칸 수 가져오기

	neg_vowels = ['ㅣ','ㅡ', 'ㅜ','ㅓ', 'ㅠ', 'ㅕ', 'ㅐ'] # 음성 모음
	pos_vowels = ['ㅗ', 'ㅏ','ㅛ', 'ㅑ'] # 양성 모음

	for i in range(1, num_rows):  
		org_word = worksheet1.cell_value(i, 0)
		pos = worksheet1.cell_value(i, 1) # pos는 그대로 사용.
		org_inf = worksheet1.cell_value(i, 2)
		org_anly = org_word+'/'+pos
		org__info = pos+' '+org_inf+' '+org_anly    
		
		
		# -P 불규칙
		if org_inf == 'VERB-P' or org_inf == 'ADJ-P': # e.g. 눕
			LOG(org__info) # 확인
			### VERB-P1 # e.g. 누우
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			list_word[-1] = '우' # 'ㅂ'을 댄신해서 '우'를 삽입한다.
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			### VERB-P2 # e.g. 누워
			if org_word == '돕' or org_word == '곱': # 예외: 돕 ---VERB-P2---> 도와
				# word
				word = split_syllables(org_word)
				list_word = list(word)
				list_word[-1] = '와'
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '2'
				# anly
				anly = word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)            
			else:
				# word
				word = split_syllables(org_word)
				list_word = list(word)
				list_word[-1] = '워'
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '2'
				# anly
				anly = org_word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)        
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')
	 

		if org_inf == 'VERB-T': # e.g. 일컫
			LOG(org__info) # 확인
			### VERB-T1 # e.g. 일컬
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			list_word[-1] = 'ㄹ'
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')


		# -L 불규칙
		if org_inf == 'VERB-L' or org_inf == 'ADJ-L': # e.g. 이끌
			LOG(org__info)
			### VERB-L1 # e.g. 이끄
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			del list_word[-1]
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')

			
		# -YE 불규칙
		if org_inf == 'VERB-YE' or org_inf == 'ADJ-YE': # e.g. 난파하
			LOG(org__info)
			### VERB-YE1 # e.g. 난파해
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			list_word[-1] = 'ㅐ'
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			### VERB-YE2 # e.g. 난파하여
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			list_word[-1] = 'ㅏ여'
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '2'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')


		# -S 불규칙
		if org_inf == 'VERB-S' or org_inf == 'ADJ-S': # e.g. 규정짓
			LOG(org__info)
			### VERB-S1 # e.g. 규정지
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			del list_word[-1]
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')

		
		# -LU 불규칙
		if org_inf == 'VERB-LU' or org_inf == 'ADJ-LU': # (르불규칙) e.g. 흐르(음성모음), 가르(양성모음) 
			LOG(org__info)
			### VERB-LU1 # e.g. 흘러(음성모음), 갈라(양성모음)
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			# 일단 맨뒤에 있는 '르' 삭제 
			del list_word[-1] 
			del list_word[-1]
			if list_word[-1] in neg_vowels: # 음성모음
				list_word[-1] = list_word[-1] + 'ㄹ러'
			elif list_word[-1] in pos_vowels: # 양성모음
				list_word[-1] = list_word[-1] + 'ㄹ라'
			word = "".join(list_word)
			word = join_jamos(word)
			if org_word == '들르': # 들르 예외처리.
				word = '들러'        
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')


		# -U 불규칙
		if org_inf == 'VERB-U' or org_inf == 'ADJ-U': # e.g. 갈겨쓰(양성모음), 가냘프(음성모음)
			LOG(org__info)
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			if len(list_word) == 2:
				list_word[-1] = 'ㅓ' # 끄,뜨,크,트는 그냥 모두 음성모음으로 처리
			else:
				del list_word[-1] # '쓰'의 'ㅡ'삭제 
				posneg_vowel = list_word[-3] + list_word[-2] # 이런식으로 segmentation 필요. 항상 [-2]가 모음이 아닐 수도 있다. 
				neg_vowel = list(set(posneg_vowel).intersection(set(neg_vowels)))
				pos_vowel = list(set(posneg_vowel).intersection(set(pos_vowels)))
				if len(neg_vowel) != 0: 
					list_word[-1] = list_word[-1] + 'ㅓ' # 음성모음이면
				else: 
					list_word[-1] = list_word[-1] + 'ㅏ' # 양성모음이면
			word = "".join(list_word)
			word = join_jamos(word)    
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) # 확인
			LOG('\n')


		# -LE 불규칙
		if org_inf == 'VERB-LE' or org_inf == 'ADJ-LE': # (러불규칙) e.g. 이르
			LOG(org__info)
			### VERB-S1 # e.g. 이르러
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			list_word += '러'
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) 
			LOG('\n')


		if org_inf == 'VERB-WU': # e.g. 푸
			LOG(org__info)
			### VERB-WU1 # e.g. 퍼
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			list_word[-1] = 'ㅓ'
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '1'
			# anly
			anly = org_word+'/'+pos
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info)
			LOG(word +' ---> '+ _info) 
			LOG('\n')


		if org_inf == 'ADJ-H': # e.g. 이렇 / 하얗/ 빨갛
			LOG(org__info)
			### ADJ-H1 # e.g. 이러 / 빨가
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			del list_word[-1] # 마지막 글자인 ㅎ 제거
			if not (list_word[-1] == 'ㅑ' or list_word[-1] == 'ㅕ'):
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '1'
				# anly
				anly = org_word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)
				LOG(word +' ---> '+ _info)  
			### ADJ-H2 # e.g. 이러 / 빨가
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			del list_word[-1] # 마지막 글자인 ㅎ 제거
			if not (list_word[-1] == 'ㅑ' or list_word[-1] == 'ㅕ'):
				list_word[-1] = 'ㅐ'
			else:
				if list_word[-1] == 'ㅑ':
					list_word[-1] = 'ㅒ'
				else: # 'ㅕ'이면..
					list_word[-1] = 'ㅖ'
			word = "".join(list_word)
			word = join_jamos(word)
			# pos -> 그대로 사용.
			# inf
			inf = org_inf + '2'
			# anly
			anly = org_word+'/'+pos # _info에는 원형단어(org_word)가 들어간다.
			_info = pos+' '+inf+' '+anly
			trie.insert(word, _info) # trie 넣을 때는 변형단어(word)를 넣는다.
			LOG(word +' ---> '+ _info) 
			LOG('\n')


		if org_inf == 'VERB-REG' or org_inf == 'ADJ-REG': # e.g. ㅗ, ㅜ, ㅣ, ㅚ
			### VERB-REG4 # e.g. 나오 -> 나와 
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			if list_word[-1] == 'ㅗ':
				LOG(org__info)
				list_word[-1] = 'ㅘ'
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '4'
				# anly
				anly = org_word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)
				LOG(word +' ---> '+ _info) # 확인
				LOG('\n')
			### VERB-REG4 # e.g. 세우 -> 세워 
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			if list_word[-1] == 'ㅜ':
				LOG(org__info)
				list_word[-1] = 'ㅝ'
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '4'
				# anly
				anly = org_word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)
				LOG(word +' ---> '+ _info) # 확인
				LOG('\n')
			### VERB-REG4 # e.g. 옮기 -> 옮겨 
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			if list_word[-1] == 'ㅣ':
				LOG(org__info)
				list_word[-1] = 'ㅕ'
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '4'
				# anly
				anly = org_word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)
				LOG(word +' ---> '+ _info) # 확인
				LOG('\n')
			### VERB-REG4 # e.g. 사람되 -> 사람돼 
			# word
			word = split_syllables(org_word)
			list_word = list(word)
			if list_word[-1] == 'ㅚ':
				LOG(org__info)
				list_word[-1] = 'ㅙ'
				word = "".join(list_word)
				word = join_jamos(word)
				# pos -> 그대로 사용.
				# inf
				inf = org_inf + '4'
				# anly
				anly = org_word+'/'+pos
				_info = pos+' '+inf+' '+anly
				trie.insert(word, _info)
				LOG(word +' ---> '+ _info) # 확인
				LOG('\n')
				

	return trie

#############################
### END of make_resuourse.py
#############################




#############
### main.py
#############

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

	
class Morph:

	def __init__(self):
		self.trie_ent = self.load('resources/ent_trie')
		self.trie_fun = self.load('resources/fun_trie')

	def load(self, name):
		return pickle.load(open(name, 'rb'))

	def extract(self, target_word):
		""" 1 ~ 6 : Segmenting using 최장일치 """
		""" 7 ~ : POS Ambiguity 해결 using 접속정보 """

		########################################
		""" 1. 모든 경우의 entry-analysis 저장 """
		########################################
		# 모음,자음단위로 나눠서(decomposition하여) 모든 경우의 조합들을 사전 lookup을 통해 뽑아낸다.
		### decomposition
		target_word = split_syllables(target_word)
		len_target_word = len(target_word)
		### lookup all entries
		# 원래 엔트리가 초성, 중성, 종성이 모두 있는데 초성, 중성까지만 있는 entry는 삭제 
		# 즉, 해당 엔트리 바로 오른쪽에 자음이 두 번 등장하는 경우 삭제 
		# (e.g. '신고전주의성진을'를 형태소 분석할 때, '시', '고저' 엔트리들은 삭제, 고려해볼 필요도 없다.)
		collect_entry_anly = [] # 모든 경우의 entry 정보가 들어감.
		#print(len_target_word)

		""" 순방향 스캔 for 엔트리-사전 """
		for i, _ in enumerate(target_word):
			for j, _ in enumerate(target_word[i:]):
				#print(target_word[i:][:j+1], i, j+i)
				if not search(self.trie_ent, target_word[i:][:j+1]) == 'No such word in Trie':
					entry = join_jamos(target_word[i:][:j+1])
					anly = search(self.trie_ent, target_word[i:][:j+1])
					collect_entry_anly.append([(entry)]+[i]+[j+i]+['ENT']+anly)     

		""" 역방향 스캔 for 기능어-사전 """
		toggle_fun = False
		#one_ch_fun = ['ㄴ','ㄹ','ㄻ','ㅁ','ㅆ']
		target_word = target_word[::-1]
		for i, _ in enumerate(target_word):
			for j, _ in enumerate(target_word[i:]):
				#print(target_word[i:][:j+1], len_target_word-1-i, len_target_word-1-j-i)
				if not search(self.trie_fun, target_word[i:][:j+1]) == 'No such word in Trie':

					#if i==0: # 기능어는 한 개만 (뒤에서부터 검색) 찾아서 넣어준다. 하지만, 기존 기능어를 포함하는 더 큰 범위의 기능어가 있으면 또 추가한다. (즉, i=0이면..) 단, 포함하지 않으면 추가하지 않는다.
					entry = join_jamos(target_word[i:][:j+1][::-1])
					anly = search(self.trie_fun, target_word[i:][:j+1])
					collect_entry_anly.append([(entry)]+[len_target_word-1-j-i]+[len_target_word-1-i]+['FUN']+anly) 

		#             if toggle_fun == False
		#                 if entry not in one_ch_fun: # 하나의 자음으로 이뤄진 기능어는 count하지 않는다. '을' 기능어에 'ㄹ'기능어가 또 있다. 이것은 나중에 다시 처리한다.
		#                     toggle_fun = True

		# 2개의 trie를 사용했지만, 하나의 dict에 저장한다.

		#################################################################
		""" 2. 전처리 (entry와 index모두 똑같은 entry-analysis 서로 병합) """
		#################################################################
		# 예를 들어, 엔트리-사전의 '신'과 기능어-사전의 '신'이 index range마저 똑같다면, 하나의 '신'으로 합쳐준다.
		# 그런데, 맨 뒷부분에서 기능어는 1개만 가지기 때문에 엔트리-사전과 겹칠일이 많치는 않다.
		# 예를 들어, 을 같은 경우는 엔트리-사전과 기능어-사전에 동시에 있고 index도 같을 수 있다. (하지만 여기서 엔트리-사전에 '을'이 없다.)
		# 윗 단에서 최대한 경우의 수를 줄여줘야 한다. 그렇지 않으면, 밑으로 갈 수록 경우의 수는 기하급수적으로 늘어날 수 있다.
		# 단, 병합할 때 같은 종류의 엔트리만 고려한다. 즉, FUN, ENT 사이의 병합은 하지 않는다. EX. '을' 같은 경우는 2가지 모두 존재한다.
		for i, _ in enumerate(collect_entry_anly):
			for j in range(0, len(collect_entry_anly)):
				if not (j == i or collect_entry_anly[j][3] != collect_entry_anly[i][3]): 
					# 자기 자신과 똑같은 친구는 빼고. 똑같은 ENT or FUN만 고려한다.
					if collect_entry_anly[i][0] == collect_entry_anly[j][0] and collect_entry_anly[i][1] == collect_entry_anly[j][1]:
						collect_entry_anly[i] += collect_entry_anly[j][4:]
						collect_entry_anly[j].insert(0, 'to-be-deleted')   

		# remove elements, which has 'to-be-deleted' in the first position
		collect_entry_anly = [elem for elem in collect_entry_anly if elem[0] != 'to-be-deleted']

		# ###############################################
		# """ 3. Longest 기능어만 살리기 (경우의 수 줄이기)"""
		# ###############################################
		# # 만약 기능어들이 같은 index range를 공유한다면, 가장 긴 기능어를 살리고 나머진 삭제한다. (우리는 기능어가 1개만 있다고 가정을 하였다.)
		# # 단, 엔트리들은 이런식으로 삭제하면 안된다. 모두 살려두어 나중에 분석결과에 모두 표시해준다.
		# # 예를 들어 'ㄹ' 기능어 (20, 20), '을' 기능어 (18, 20)가 있는 경우 'ㄹ' 기능어를 삭제한다.
		# filtered_fun = [i for i in collect_entry_anly if i[3] == 'FUN'] # filtering only fun
		# filt_sorted_fun = sorted(filtered_fun, key = lambda x: len(split_syllables(x[0])))
		# for i, _ in enumerate(filt_sorted_fun):
		#     target = filt_sorted_fun[i]
		#     for j in range(i+1, len(filt_sorted_fun)):
		#         ref = filt_sorted_fun[j]
		#         if int(ref[1]) <= int(target[1]):# and int(ref[2]) >= int(target[2]):
		#             filt_sorted_fun[i].insert(len(filt_sorted_fun[i]), 'to-be-deleted') # add on last position

		# # remove elements, which has 'to-be-deleted' in the last position
		# filt_sorted_fun = [elem for elem in filt_sorted_fun if elem[-1] != 'to-be-deleted']            

		# # merge
		# filtered_ent = [i for i in collect_entry_anly if i[3] == 'ENT'] # filtering only fun
		# final_collect_entry_anly = filtered_ent + filt_sorted_fun

		final_collect_entry_anly = collect_entry_anly[:]
		###################################################################################
		""" 4. 엔트리 중 내 바로 오른쪽 index가 비어있는 경우 해당 엔트리 지우기 (경우의 수 줄이기)"""
		###################################################################################
		# 예를 들어, 신고전주의정신을 -> 시, 저, 중 은 삭제된다. 다음 index가 비어있기 때문에
		for i, _ in enumerate(final_collect_entry_anly):
			tnk = False
			for j in range(0, len(final_collect_entry_anly)):
				if final_collect_entry_anly[i][2]+1 ==  final_collect_entry_anly[j][1]:
					tnk = True
				elif final_collect_entry_anly[i][2]+1 == len_target_word:
					tnk = True
			if tnk == False:
				final_collect_entry_anly[i].insert(0, 'to-be-deleted')

		# remove elements, which has 'to-be-deleted' in the first position        
		final_collect_entry_anly = [elem for elem in final_collect_entry_anly if elem[0] != 'to-be-deleted']

		#########################################################################
		""" 5. 조합하기 (엔트리 묶음으로 즉, 엔트리 종류는 1개라고 가정한다 여기서는..) """
		#########################################################################
		# 조합하는 과정에서, 띄어쓰기 오류 또는 신조어 오류를 확인할 수 있다.
		# 오류확인 1. sorting 후에 마지막 element의 start index가 target_word의 길이와 맞지 않을 경우.

		# sorting based on start index
		final_collect_entry_anly = sorted(final_collect_entry_anly, key = lambda x: int(x[1]))

		# 오류확인 1. 처음과 끝의 경계는 아래와 같이 체크하면 된다. (중간에 있는 오류는 다음단계에서 확인한다.)
		assert(final_collect_entry_anly[0][1] == 0) # 처음이 index 0으로 시작하지 않을 경우.
		assert(final_collect_entry_anly[-1][2] == len_target_word-1) # 마지막이 word길이만큼의 index가 아닐 경우.

		### merging / combining all cases using recursive function
		list_global_cases, path = [], []
		# filtering only index0 (Starting point to recursive function)
		index0_entry_anly_set = [ele for ele in final_collect_entry_anly if int(ele[1]) == 0] # first position
		# recursive merging
		recursive_merging(final_collect_entry_anly, index0_entry_anly_set, path, list_global_cases)

		# 오류확인 2. 처음부터 끝까지 이어지는 하나의 case도 없을 경우.
		fullpath_check = False
		for i in range(0, len(list_global_cases)):
			if list_global_cases[i][-1][2]+1 == len_target_word:
				fullpath_check = True
		assert(fullpath_check == True) # 오류 난다면 사전 lookup 문제이다
		
		
		### Sequence가 0에서부터 len_target_word-1까지 이어지지 않으면 삭제한다.
		for i, seq in enumerate(list_global_cases):
			if seq[0][1] != 0 or seq[-1][2] != len_target_word-1:
				list_global_cases[i] = 'to-be-deleted'
		# remove elements, which has 'to-be-deleted' in the first position        
		list_global_cases = [elem for elem in list_global_cases if elem != 'to-be-deleted']
		
		#######################################################
		""" 6. 형태소 조합에서 기능어가 있을 때, 마지막에 없는 경우는 삭제하자. """
		#######################################################
		# 즉, FUN이 2번 연속 등장하는 경우는 삭제된다
		for i, case in enumerate(list_global_cases):
			case_len = len(case)
			for j, entry in enumerate(case):
				if case[j][3] == 'FUN':
					if j!=case_len-1: # FUN이 마지막에 있지 않은 경우...
						#print(entry)
						list_global_cases[i] = 'to-be-deleted'
		# filtering
		list_global_cases = [case for case in list_global_cases if case != 'to-be-deleted']
		

	#     longest = False # longest는 항상하지 않는다.
	#     if longest == True:
	#         ##################################################
	#         """ 6. 최장길이 우선으로 정렬하고 상위 1개만 보이자. """
	#         ##################################################
	#         # 위의 print 내용을 보다시피 경우의 수가 많다. 더군다나 entry 종류까지 unfolding하면 경우의 수가 매우 많이 증가한다.
	#         # 따라서, '최장일치' 우선순위 조건을 부여해, 길이가 긴 순서대로 정렬한 후 상위 1개까지만 확인하자.
	#         temp_summed_squared = [0] * len(list_global_cases)
	#         for i, case in enumerate(list_global_cases):
	#             # 최장일치 기준: 모든 엔티티 길이의 제곱들을 각각 더한 값이 제일 큰 case가 최장일치가 된다.
	#             # 모든 엔티티길이를 고려한 이유: maximum길이를 가지는 엔티티만 고려하면 중복인 경우가 생긴다.
	#             # 제곱을 한 이유: maximum길이를 가지는 엔티티는 똑같을 때, 다른 엔티티의 길이가 1인 2개와, 2인 1개가 있을 경우, 2에 더 가중치를 주기 위해 제곱한다.
	#             for j, entity in enumerate(case):
	#                 temp_summed_squared[i] += (len(split_syllables(case[j][0])) * len(split_syllables(case[j][0]))) # 제곱

	#         max_value = max(temp_summed_squared)
	#         max_info_cases = []

	#         for i, value in enumerate(temp_summed_squared):
	#             if value == max_value:
	#                 max_info_cases.append(list_global_cases[i])

	#         ### 의문점: 최장길이 우선으로 상위 1개를 선택하는데, 이런 경우 접속정보를 사용하지 않아도 항상 정상적인 연결이 되는가?
	#     else:
		max_info_cases = list_global_cases[:]
			
		# 접속정보 LOAD하기
		wb_connect_info = xlrd.open_workbook('assets/connect_info.xlsx') 
		ws_entent = wb_connect_info.sheet_by_name('내용어끼리')
		num_rows = ws_entent.nrows #줄 수 가져오기
		num_cols = ws_entent.ncols #칸 수 가져오기

		entent_lookup = []
		for i in range(1, num_rows):
			entent_lookup.append(ws_entent.cell_value(i, 0)+' '+ws_entent.cell_value(i, 1))
			#print(ws_entent.cell_value(i, 0), ws_entent.cell_value(i, 1))
		#     word = worksheet1.cell_value(i, 0)
		#     pos = worksheet1.cell_value(i, 1)
		#     inf = worksheet1.cell_value(i, 2)
		#     anly = word+'/'+pos
		#     _info = pos+' '+inf+' '+anly
		#     trie.insert(word, _info) # word는 insert함수에 의해 decomposition된다.
		# print('>> Store 엔트리-사전 Corpus to Trie, Complete !!')  

		#wb_connect_info = xlrd.open_workbook('connect_info.xlsx') 
		ws_entfun = wb_connect_info.sheet_by_name('내용어와기능어')
		num_rows = ws_entfun.nrows #줄 수 가져오기
		num_cols = ws_entfun.ncols #칸 수 가져오기

		entfun_lookup = []
		for i in range(1, num_rows):
			entfun_lookup.append(ws_entfun.cell_value(i, 0)+' '+ws_entfun.cell_value(i, 1)+' '+ws_entfun.cell_value(i, 2))
			#print(ws_entent.cell_value(i, 0), ws_entent.cell_value(i, 1))
		#     word = worksheet1.cell_value(i, 0)
		#     pos = worksheet1.cell_value(i, 1)
		#     inf = worksheet1.cell_value(i, 2)
		#     anly = word+'/'+pos
		#     _info = pos+' '+inf+' '+anly
		#     trie.insert(word, _info) # word는 insert함수에 의해 decomposition된다.
		# print('>> Store 엔트리-사전 Corpus to Trie, Complete !!')  

		# 원형 전처리 (ex. VERB-S0 -> VERB-S) 위의 불규칙 사전 등록시에 원형에 0번호는 입력하지 않아서 여기서 빼줘야 한다.
		for i, entry in enumerate(entfun_lookup):
			if list(entry.split()[0])[-1] == '0':
				temp_list = list(entry.split()[0])
				del temp_list[-1]
				temp_list = "".join(temp_list)
				entfun_lookup[i] = temp_list+' '+entry.split()[1]+' '+entry.split()[2]

		##############################################################
		""" 7. 각각의 엔티티의 pos의 경우의 수를 줄이자. (접속 정보 사용) """
		##############################################################
		# 만약에 case들이 단 하나의 entry로 구성되어있다면 이 단계는 필요없다.
		# 이제 하나의 case을 얻었으니, 각각의 엔티티의 pos의 경우의 수를 줄이자. 보통 하나의 엔티티는 여러개 종류의 pos를 가진다. 이것을 그대로 펼치면 경우의 수가 또 많아진다.
		# segmenting을 하기전에 pos ambiguity를 해결해도 된다. 하지만, 계산량이 엄청날 것이다.

		list_delete_idx = []

		for i, case in enumerate(max_info_cases):    
			if len(max_info_cases[i]) != 1: # 단 하나의 entry로 구성되어있다면 이 단계는 필요없다. 이웃 entry가 아예 없기 때문이다.

				### FUN이 있는 경우랑 없는 경우랑 나눈다. 있으면 FUN Scanning을 해야되니까..
				filtered_fun = [i for i in max_info_cases[i] if i[3] == 'FUN']
				
				"""
				# FUN이 한개도 없는 경우
				if len(filtered_fun) == 0:

					# RIGHT-scanning
					for j, entry in enumerate(max_info_cases[i]): 
						if not j==len(max_info_cases[i])-1: # except for last one
							entry_list_t0 = max_info_cases[i][j][4:]
							entry_list_t1 = max_info_cases[i][j+1][4:]

							for m, anly_info_t0 in enumerate(entry_list_t0):
								tkn = False
								pos_t0 = max_info_cases[i][j][4:][m].split()[0]
								#print(pos)
								for n, anly_info_t1 in enumerate(entry_list_t1):
									pos_t1 = max_info_cases[i][j+1][4:][n].split()[0]
									temp = pos_t0+' '+pos_t1

									if temp in entent_lookup:
										tkn = True

								if tkn == False and len(entry_list_t0)!=1:
		#                             print(len(entry_list_t0))
		#                             print(max_info_cases[i][j][4:][m]) 
		#                             print('->', pos_t0, pos_t1)
									tuple_ = (i, j, m)
									list_delete_idx.append(tuple_)
									#print(temp)                            



					# LEFT-scanning        
					for j, entry in reversed(list(enumerate(max_info_cases[i]))):
						#print(j, entry)
						if not j==0: # except for first one
							entry_list_t0 = max_info_cases[i][j][4:]
							entry_list_tmin1 = max_info_cases[i][j-1][4:]
							#print(entry_list_t0)

							for m, anly_info_t0 in enumerate(entry_list_t0):
								tkn2 = False
								pos_t0 = max_info_cases[i][j][4:][m].split()[0]
								#print(pos)
								for n, anly_info_tmin1 in enumerate(entry_list_tmin1):
									pos_tmin1 = max_info_cases[i][j-1][4:][n].split()[0]
									temp = pos_tmin1+' '+pos_t0

									if temp in entent_lookup:
										tkn2 = True

								if tkn2 == False and len(entry_list_t0)!=1:
		#                             print(len(entry_list_t0))
		#                             print(max_info_cases[i][j][4:][m])
		#                             print('<-', pos_tmin1, pos_t0)
									tuple_ = (i, j, m)
									list_delete_idx.append(tuple_)
									#print(temp)                           
					"""

				# FUN이 한개라도 있는 경우
				if len(filtered_fun) != 0:
					
					"""
					# RIGHT-scanning (마지막 1개는 scan하지 않는다.) 
					for j, entry in enumerate(max_info_cases[i]): 
						if not (j==len(max_info_cases[i])-2 or j==len(max_info_cases[i])-1): # except for last one
							entry_list_t0 = max_info_cases[i][j][4:]
							entry_list_t1 = max_info_cases[i][j+1][4:]

							for m, anly_info_t0 in enumerate(entry_list_t0):
								tkn = False
								pos_t0 = max_info_cases[i][j][4:][m].split()[0]
								#print(pos)
								for n, anly_info_t1 in enumerate(entry_list_t1):
									pos_t1 = max_info_cases[i][j+1][4:][n].split()[0]
									temp = pos_t0+' '+pos_t1

									if temp in entent_lookup:
										tkn = True

								if tkn == False and len(entry_list_t0)!=1:
		#                             print(len(entry_list_t0))
		#                             print(max_info_cases[i][j][4:][m]) 
		#                             print('->', pos_t0, pos_t1)
									tuple_ = (i, j, m)
									list_delete_idx.append(tuple_)
									#print('RIGHT===',temp, tuple_)              


					# LEFT-scanning (마지막 2번째부터 시작한다.) 
					for j, entry in reversed(list(enumerate(max_info_cases[i]))):
						#print(j, entry)
						if not (j==0 or j==len(max_info_cases[i])-1):
							entry_list_t0 = max_info_cases[i][j][4:]
							entry_list_tmin1 = max_info_cases[i][j-1][4:]
							#print(entry_list_t0)

							for m, anly_info_t0 in enumerate(entry_list_t0):
								tkn2 = False
								pos_t0 = max_info_cases[i][j][4:][m].split()[0]
								#print(pos)
								for n, anly_info_tmin1 in enumerate(entry_list_tmin1):
									pos_tmin1 = max_info_cases[i][j-1][4:][n].split()[0]
									temp = pos_tmin1+' '+pos_t0

									if temp in entent_lookup:
										tkn2 = True

								if tkn2 == False and len(entry_list_t0)!=1:
		#                             print(len(entry_list_t0))
		#                             print(max_info_cases[i][j][4:][m])
		#                             print('<-', pos_tmin1, pos_t0)
									tuple_ = (i, j, m)
									list_delete_idx.append(tuple_)
									#print('LEFT===',temp, tuple_)            
					"""
					
					############################################################################# FUN처리
					# RIGHT-scanning
					for j, entry in enumerate(max_info_cases[i]):
						if j==len(max_info_cases[i])-2:

							entry_list_ref = max_info_cases[i][j][4:]
							entry_list_comp = max_info_cases[i][j+1][4:]
							#print(entry_list_t0)

							for m, anly_info_ref in enumerate(entry_list_ref): # 기준
								tkn3 = False
								pos_ref = max_info_cases[i][j][4:][m].split()[0]
								inf_ref = max_info_cases[i][j][4:][m].split()[1]
								#print(pos)
								for n, anly_info_comp in enumerate(entry_list_comp):
									pos_comp = max_info_cases[i][j+1][4:][n].split()[0]
									inf_comp = max_info_cases[i][j+1][4:][n].split()[1]
									temp = inf_ref+' '+pos_comp+' '+inf_comp
									#print(temp, '[right]')
									if temp in entfun_lookup:
										tkn3 = True

								if tkn3 == False and len(entry_list_ref)!=1:
		#                             print(len(entry_list_t0))
		#                             print(max_info_cases[i][j][4:][m])
		#                             print('<-', pos_tmin1, pos_t0)
									tuple_ = (i, j, m)
									list_delete_idx.append(tuple_)
									#print('[FUN] right------------>', temp, tuple_)                     


					# LEFT-scanning
					for j, entry in reversed(list(enumerate(max_info_cases[i]))):
						#print(j, entry)
						if j==len(max_info_cases[i])-1: 
							entry_list_ref = max_info_cases[i][j][4:]
							entry_list_comp = max_info_cases[i][j-1][4:]
							#print(entry_list_t0)

							for m, _ in enumerate(entry_list_ref): # 기준
								tkn4 = False
								ref_pos = max_info_cases[i][j][4:][m].split()[0]
								ref_inf = max_info_cases[i][j][4:][m].split()[1]
								#print(pos)
								for n, _ in enumerate(entry_list_comp):
									comp_inf = max_info_cases[i][j-1][4:][n].split()[1]
									temp = comp_inf+' '+ref_pos+' '+ref_inf # LEFT-scanning이기 때문에...
									#print(temp, '[left]')
									if temp in entfun_lookup:
										tkn4 = True

								if tkn4 == False and len(entry_list_ref)!=1:
		#                             print(len(entry_list_t0))
		#                             print(max_info_cases[i][j][4:][m])
		#                             print('<-', pos_tmin1, pos_t0)
									tuple_ = (i, j, m)
									list_delete_idx.append(tuple_)
									#print('[FUN] left------------>', temp, tuple_)     


		list_delete_idx = list(set(list_delete_idx))[:] # A set is guaranteed to not have duplicates.
		list_delete_idx = sorted(list_delete_idx, key=lambda x: (int(str(x[0])+str(x[1])+str(x[2]))), reverse=True)

		for index_set in list_delete_idx:
			i = index_set[0]
			j = index_set[1]
			m = index_set[2]
		#     print(i, j, m)

		#     print(max_info_cases[i][j][4:])
		#     print(max_info_cases[i][j][4:][m])
			filtered = [elem for elem in max_info_cases[i][j][4:] if elem != max_info_cases[i][j][4:][m]]
		#     print(filtered)
		#     print(max_info_cases[i][j])
		#     print(max_info_cases[i][j][0:4] + filtered)
		#     print('\n')

			max_info_cases[i][j] = max_info_cases[i][j][0:4] + filtered
			#max_info_cases[i][j] = max_info_cases[i][j][0:3]+filtered

			
		#return max_info_cases

		##############################################################
		""" 8. 하나의 엔트리라도 형태소 추출 실패한 경우 해당 case 삭제하기 """
		##############################################################        
		fail = False
		failure_check = [0] * len(max_info_cases)
		for i, case in enumerate(max_info_cases):
			for j, entry in enumerate(case):
				if len(entry)==4:
					fail = True
			if fail == True:
				failure_check[i] = 1

			fail = False
		
		list_finalresult = []
		for i, case in enumerate(max_info_cases):
			if failure_check[i] == 0:
				list_finalresult.append(case)
					
			
		####################################################################
		""" (Optional) 9. 엔트리개수와 각각 index range가 모두 똑같으면 삭제 """ 
		####################################################################
		# pos tagging할 때, 경우의 수가 많아지니까 그냥 똑같으면 삭제하자. (기존에서는 다 똑같더라도 ENT와 FUN이 다르면 또 List에 넣었다)
		
		def check_euqal(cur_case, unique_list_finalresult):
			token = False
			
			for case in unique_list_finalresult:
				token = False # initialization
				
				for j, ent in enumerate(case):
					if len(cur_case) == len(case):
						if cur_case[j][0] == case[j][0]:
							token = True # 처음부터 끝까지 true된다면: true가 될 수 있음.
						else:
							break # 한번이라도 false된다면 게임 끝.
					else:
						break

				if token == True:
					return True # True: 같은 것이 1개라도 있음
				
			return False # False: 같은 것이 1개라도 없음
		
		
		unique_list_finalresult = []
		for case in list_finalresult:
			if check_euqal(case, unique_list_finalresult) == False:
				unique_list_finalresult.append(case)
		
			
	#     return list_finalresult
		return unique_list_finalresult





		
		
		











