# 한국어 형태소분석 및 품사태깅

## 형태소 분석기 (사전/규칙기반 모델)
* Lexicon: 엔트리(체언,용언)사전 / 기능어(조사,어미)사전 (불규칙 사전 구축을 위한 inflection정보) 
* Morphotactics: 형태소 결합 규칙 리스트 (ex. 명사+어미(x), 형용사+어미(o))
* Orthographic rules: 불규칙 사전 또는 확장 사전 (하나의 stem에서 변하는 단어들이 많음)
* 한국어 특성에 맞게 사전검색을 효율적으로 하기 위해 trie 자료구조를 사용해 사전을 구축
* 사전과 결합규칙에 맞는 모든 경우의 수의 형태소 조합들을 출력한다. 최적의 형태소 조합 1개는 품사 태깅과 함께 확률적으로 선택

## 품사 태거 (corpus기반 확률 모델)
* 조건부 확률 (태그|단어) 모델링으로 단어에 대한 태그 예측
* 확률을 count-base로 corpus로부터 inference하기 위해 bayes rule과 markov assumption 사용
* 중복된 계산을 피하기 위해 dynamic programming (i.e. viterbi) 사용
* 영어와 달리 형태소 조합이 여러개 있는 한국어 특성상 품사 태깅에서 태깅과 동시에 가장 좋은 형태소 조합을 선택

## 요구사항
* Python 3.5
* [Hangul-utils](https://github.com/kaniblu/hangul-utils)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## 사용법 
* 엑셀파일로부터 trie기반 엔트리/기능어 lookup table 생성
* 세종코퍼스로부터 smoothing된 pos전이확률, pos로부터word출력확률 lookup table 생성 
* (주의) 세종코퍼스 수정필요: 'ᆫ'을 'ㄴ'으로 고쳐야함.
```
python make_resources.py
```
* 분석하고 싶은 문장을 인자로 main 함수를 실행한다.
```
python main.py 매일 아침 아프리카에선 당신은 잠에서 깨어난다
```

## 예시
![](assets/example.png)

## 제한사항
* 입력은 오로지 한글만 가능 (숫자, 콤마 등은 x)
* Light한 엔트리/기능어 사전때문에 많은 단어들을 커버하지 못함 (오류: assert(fullpath_check == True))
* 형태소 분석기 TERMINABLE 처리 하지 않음 (ex. 어/EC, 아/EC)
* 알고리즘 최적화를 실시하지 않음 (속도문제 발생)

## 향후과제
* 제한사항 보완
* 형태소 분석기 보완
   * 오타처리
   * 띄어쓰기 오류처리
   * 신조어처리

## 감사
충남대학교, 자연어처리



