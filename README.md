# ARS-system-for-protecting-telephone-counselor
Telmet - 전화 상담원 보호를 위한, 언어폭력 탐지시 자동으로 종료하는 ARS 시스템

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

+ 고객,상담원의 발화를 실시간으로 탐지 --> **STT를 활용해** 스트리밍 보이스를 처리하는 **실시간 처리 모듈** 개발 
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
본 시스템에서는 SKTBrain에서 제공하는 [KoBERT](https://github.com/SKTBrain/KoBERT) 모델을 미세 조정한 다중 분류기를 개발  
시스템 평가에는 (선제적 사전 매칭 + 다중 분류기) 처리 결과를 바탕으로 평가하였다

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

<br>

## Output View
### 1. Main Page
![image](https://github.com/82KJ/ARS-system-for-protecting-telephone-counselor/assets/45115733/771b0f94-11ef-4e9e-89c9-fc27680d537d)
+ **L1** : **Telemt 시작 버튼** - ChatRoom Page로 이동하여 Telemt을 시작한다&nbsp;&nbsp;&nbsp;  
  
### 2. ChatRoom Page
![image](https://github.com/82KJ/ARS-system-for-protecting-telephone-counselor/assets/45115733/793c4cd9-21ef-46fd-bf82-bf507532b0f2)
+ **L1** : **녹음 시작 버튼** - 고객과 상담원의 실시간 발화를 시스템으로 전달한다&nbsp;&nbsp;&nbsp;  

![image](https://github.com/82KJ/ARS-system-for-protecting-telephone-counselor/assets/45115733/8696fd09-966e-4ed3-b838-8ee514b06c42)
+ **L1** : **폭언 탐지** - 발화에서 폭언이 감지되면, 빨강색으로 마킹&nbsp;&nbsp;&nbsp;  
+ **L2** : **성희롱 탐지** - 발화에서 성희롱이 감지되면, 파랑색으로 마킹&nbsp;&nbsp;&nbsp;  
+ **L3** : **Result Page 이동 버튼** - Result Page로 이동하여, 결과를 확인한다 &nbsp;&nbsp;&nbsp;  

### 3. Result Page
![image](https://github.com/82KJ/ARS-system-for-protecting-telephone-counselor/assets/45115733/2e2b3df8-917d-4e6d-846e-0baac87c05e3)
+ **L1** : **강제 종료 여부** - 강제 종료시 Shutdown, 정상 종료시 Normal&nbsp;&nbsp;&nbsp;  
+ **L2** : **전체 문장 개수** - STT를 통해 변환된 전체 문장 개수&nbsp;&nbsp;&nbsp;  
+ **L3** : **녹음 시간** - 전체 발화 녹음 시간 &nbsp;&nbsp;&nbsp;  
+ **L4** : **전체 요약 표** - 전체 발화의 탐지 결과를 표로 요약하여 제시 &nbsp;&nbsp;&nbsp;  

### 3. ChatRoom Page - Other Situation
![image](https://github.com/82KJ/ARS-system-for-protecting-telephone-counselor/assets/45115733/82d469af-4270-45c1-a9ab-a24a1697f163)
+ **L1** : **문맥 의미 파악을 통한 폭언 탐지** - 특정 폭언 키워드 없이도 전체 문맥으로 폭언 탐지 상황 &nbsp;&nbsp;&nbsp;  
+ **L2** : **상담원 발화 사전 매칭** - 상담원 발화 사전 매칭 후 2차 검증 상황&nbsp;&nbsp;&nbsp;  

<br>

## User Manaul
- 시연 영상 : https://youtu.be/JJABFTkqWOA
- 설치 매뉴얼 : https://youtu.be/e6OmU-yuZIQ
- 본 시스템은 실시간 STT를 위해 [VITO Speech](https://developers.vito.ai/?utm_source=vito_homepage&utm_medium=%EB%AC%B4%EB%A3%8C_click&utm_campaign=family_site_%EC%83%81%EB%8B%A8_api) API를 활용합니다.
  사이트에 방문해서 필요한 제원을 받아주세요
- 현재 모델 다운로드 링크는 비공개로 전환하였습니다. 필요하신 분들은 아래의 이메일을 통해 연락 주세요

<br>

## Contacts
프로젝트 관련 문의는 다음의 이메일을 이용해 주시기 바랍니다.  
E-mail : remf123@gmail.com
