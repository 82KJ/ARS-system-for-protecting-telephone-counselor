# ARS-system-for-protecting-telephone-counselor
전화 상담원 보호를 위한, 언어폭력 탐지시 자동으로 종료하는 ARS 시스템

<br>

## 기술 스택
> <img src="https://img.shields.io/badge/Django%20Channels-092E20?style=for-the-badge&logo=django&logoColor=white">  
> <img src="https://img.shields.io/badge/sqlite3-00599C?style=for-the-badge&logo=sqlite&logoColor=white">    
> <img src="https://img.shields.io/badge/pytorch-F80000?style=for-the-badge&logo=pytorch&logoColor=white">  
> <img src="https://img.shields.io/badge/KoBERT-F05032?style=for-the-badge&logo=buffer&logoColor=white">
> <img src="https://img.shields.io/badge/vito%20speech-7952B3?style=for-the-badge&logo=teamspeak&logoColor=white">

<br>

## 개발 멤버
+ **Team Leader**
  + [Byabya](https://github.com/noyesachopppp) - FE / KoBERT Fine Tuning / Data Preprocessing / Testing & Results Analysis
+ **Team Member**
  + [KwanJung98](https://github.com/82KJ/) - FE / BE / KoBERT Fine Tuning / Data Preprocessing / Testing & Results Analysis
  + [penpenguin2018](https://github.com/penpenguin2018) - BE / Audio Meta Data Processing / Data Preprocessing / Testing & Results Analysis
  + [Yunel7](https://github.com/Yunel7) - BE / Audio Meta Data Processing / Data Preprocessing / Testing & Results Analysis

<br>
  
## 개요 
**전화 상담원을 고객의 언어폭력으로부터 보호**하기 위해 언어폭력에 대한 경고 및 강제 종료라는 방안이 시행되고 있지만, 주관적인 판단으로 인한 강제 종료는 부정적인 업무 평가와 같은 다양한 불이익을 발생시켜 현장에서는 잘 활용되지 않는다.  
따라서 본 시스템은 **사전 매칭과 인공지능 분류를 기반으로 하는 언어폭력 탐지 시스템**을 제시하여, 객관적인 강제 종료를 수단을 제공한다

+ 고객,상담원의 발화를 실시간으로 탐지 --> 스트리밍 보이스를 처리하는 **실시간 처리 모듈** 개발 
+ 일반 발화의 언어폭력 오분류 최소화 --> **선제적 사전 매칭**을 통한 1차 필터링 진행
+ 언어폭력 탐지 정확도의 최대화 --> **사전, 음성메타 정보, 인공지능 분류** 다양한 수단 활용
+ 폭언, 성희롱 등 다양한 언어폭력 탐지 --> 인공지능 **다중 분류기** 개발

<br>
