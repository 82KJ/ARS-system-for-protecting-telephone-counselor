# ARS-system-for-protecting-telephone-counselor
전화 상담원 보호를 위한, 언어폭력 탐지시 자동으로 종료하는 ARS 시스템

<br>

## Tech Stacks
> <img src="https://img.shields.io/badge/Django%20Channels-092E20?style=for-the-badge&logo=django&logoColor=white">  
> <img src="https://img.shields.io/badge/sqlite3-00599C?style=for-the-badge&logo=sqlite&logoColor=white">    
> <img src="https://img.shields.io/badge/pytorch-F80000?style=for-the-badge&logo=pytorch&logoColor=white">  
> <img src="https://img.shields.io/badge/KoBERT-F05032?style=for-the-badge&logo=buffer&logoColor=white">
> <img src="https://img.shields.io/badge/vito%20speech-7952B3?style=for-the-badge&logo=teamspeak&logoColor=white">

<br>

## Project Members
+ **Team Leader**
  + [Byabya](https://github.com/noyesachopppp) - FE / KoBERT Fine Tuning / Data Preprocessing / Testing & Results Analysis
+ **Team Member**
  + [KwanJung98](https://github.com/82KJ/) - FE / BE / KoBERT Fine Tuning / Data Preprocessing / Testing & Results Analysis
  + [penpenguin2018](https://github.com/penpenguin2018) - BE / Audio Meta Data Processing / Data Preprocessing / Testing & Results Analysis
  + [Yunel7](https://github.com/Yunel7) - BE / Audio Meta Data Processing / Data Preprocessing / Testing & Results Analysis

<br>
  
## Summary 
**전화 상담원을 고객의 언어폭력으로부터 보호**하기 위해 언어폭력에 대한 경고 및 강제 종료라는 방안이 시행되고 있지만, 상담원의 주관적인 판단으로 인한 강제 종료는 부정적인 업무 평가와 같은 다양한 불이익을 발생시키기에 실제 현장에서는 잘 활용되지 않는다.  
따라서 본 시스템은 **사전 매칭과 인공지능 분류를 기반으로 하는 언어폭력 탐지 시스템**을 제시하여, 객관적인 강제 종료를 수단을 제공한다

+ 고객,상담원의 발화를 실시간으로 탐지 --> 스트리밍 보이스를 처리하는 **실시간 처리 모듈** 개발 
+ 일반 발화의 언어폭력 오분류 최소화 --> **선제적 사전 매칭**을 통한 1차 필터링 진행
+ 언어폭력 탐지 정확도의 최대화 --> **사전, 음성메타 정보, 인공지능 분류** 다양한 수단 활용
+ 폭언, 성희롱 등 다양한 언어폭력 탐지 --> 인공지능 **다중 분류기** 개발

<br>

## Data Set
### 1. Training Data Set
AIHUB에서 제공하는 '텍스트 윤리검증 데이터'를 활용하여, 중복 표현, 초성, 이모티콘 등 제거 및 각색 전처리 진행
|종류|라벨|개수|
|:---:|:---:|:---:|
|일반|0|20,000|
|폭언|1|8,677|
|성희롱|2|10,166|  

= **총 38,843 문장**

### 2. Dictionary Data Set
Training Data Set을 기준으로 각 문장별 핵심 언어폭력 형태소 키워드를 추출하여 사전 형식으로 저장   
또한, 상담원 언어폭력 대응 매뉴얼를 활용하여 상담원 형태소 키워드를 추출하여 사전 형식으로 저장  
(형태소 분석기는 [Kiwi](https://github.com/bab2min/Kiwi)를 사용)
|종류|개수|
|:---:|:---:|
|폭언|5,693|
|성희롱|3,691|
|상담원|38|

= **총 9,422 키워드**

<br>

## System Evaluation
전체 데이터 38,843문장 중 90%를 훈련 데이터, 10%를 테스트 데이터로 하여 전체 시스템의 성능을 측정  
(볼드 처리된 수치는 단순 모델만을 이용한 수치보다 향상된 수치)
||일반/폭언/성희롱|
|:---:|:---:|
|Precision|0.942/**0.917/0.916**|
|Recall|**0.967**/0.896/0.887|
|F1 measure|**0.954**/0.906/0.901|
|Accuracy|**0.931**|

= **일반 문장의 주요 성능 지표에서 높은 성능을 확인 가능**

<br>

||일반|폭언|성희롱|
|:---:|:---:|:---:|:---:|
|분류 모델|1912|54|33|
|사전매칭 + 분류 모델|1933|39|27|

= 구체적으로, 선제적 사전매칭을 이용한 전체 시스템이 모델에서 **오분류한 87개의 일반문장 중 21개를 감소**시킴








