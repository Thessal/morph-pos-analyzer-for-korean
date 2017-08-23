from morph_analysis import * # for just printf
from pos_tagging import pos_tagging
import pickle
import sys


arg_str = ' '.join(sys.argv[1:])

#

morph_class = Morph()


#sent = '우선 신고전주의정신을 본받자'
sent = arg_str



# 형태소 분석 결과값을 보여주기 위해 형태소 분석기를 따로 한 번 더 돌리자.
print('\n')
print('********** Morph Analyzer Result **********')
print('\n')
splited_sent = sent.split()
for i, token in enumerate(splited_sent):
	morph_result = morph_class.extract(token)
	for j, case in enumerate(morph_result):
		temp_entry_list = ''
		for k, entry in enumerate(case):
			temp_entry_list += entry[0]
			if k != len(case)-1:
				temp_entry_list += ' + '
		
		print('   ',temp_entry_list)
	print('\n')
print('*******************************************')


###########################	
""" 형태소 분석 & 품사 태깅 """
###########################
print('\n')
print('********** Morph & POS Result **********')
print('\n')
print('   ', pos_tagging(sent))
print('\n')
print('*******************************************')








