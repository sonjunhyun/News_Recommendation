### 컨텐츠 기반 필터링(Doc2Vec)을 이용한 
# 📰 경제 뉴스 기사 추천 시스템
<br/><br/>
## 1. Outline
![image](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/87634594/771161cf-d1b0-453c-9a39-df0b1058ea9f)

<br/><br/><br/>
## 2. Period & Process
![process](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/73fe9ed9-c3f3-4555-ae11-9d7f8118445e)
<br/><br/><br/>
> ## Main Process

### 1) Crawling - Scrapy
<img src="https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/118335520/c71dbb19-88cc-4852-8f6f-f2d5701e83e8" width="500" height="250"/>

- Python 기반의 오픈 소스 웹 크롤링 및 스크레이핑 프레임워크
- 대규모 스크래핑에 적합, 동시에 여러 요청 처리 가능

<br/><br/><br/>
① [다음 경제 뉴스 기사](https://news.daum.net/breakingnews/economic)

- 수집기간 : _2023년 06월 13일 ~ 2023년 09월 13일 (3개월)_
- 소분류 : 금융, 기업산업, 취업직장인, 경제일반, 자동차, 주식, 시황분석, 공시, 해외증시, 채권선물, 외환, 주식일반, 부동산, 생활경제, 국제경제
- 수집내용 : 제목, 기자, 언론사, 본문, 작성일자, 수정일자, 스티커, url
- **기사 347,759건**  
<br/>

② [네이버 경제 뉴스 기사](https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101)

- 수집기간 : _2023년 06월 13일 ~ 2023년 09월 13일 (3개월)_
- 소분류 : 금융, 증권, 산업/재계, 중기/벤처, 부동산, 글로벌 경제, 생활경제, 경제 일반
- 수집내용 : 제목, 기자, 언론사, 본문, 작성일자, 수정일자, 스티커, url, 댓글(유저 id, 유저 닉네임, 작성일자, 좋아요 수, 싫어요 수)
- **기사 457,817건,  댓글 1,928,758건**

<br/><br/>
### 2) Pre-processing

- 날짜 형식의 컬럼은 datetime 형식으로 변환, 네이버&다음 날짜 형식 통일
- 제목(title) 또는 본문(content)이 결측치인 row 제거
- 본문 글자 수가 50자 미만인 row 제거
- 제목에 '부고'와 '단신'과 같은 경제와 직접적인 연관이 없는 키워드를 포함하는 row 제거

<br/><br/>
### 3) Modeling - Gensim

<img src="https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/1e053994-9d80-4028-ba7e-a7339f1b98d1" width="500" height="250"/>

- 자연어를 벡터로 변환하는 데 필요한 편의 기능을 제공하는 라이브러리
- Word2Vec, Doc2Vec 함수 포함
- 뉴스 본문 tokenization (simple_preprocess)
- TaggedDocument 생성 → Doc2Vec 모델 생성 및 학습

<br/><br/>
### 4) Model Application Results

- 기사 url 입력 → 본문과 유사한 뉴스 10개 추천

![url](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/977f7471-2071-4250-9818-39aa2fffd379)


![recommend](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/a95e99f1-a4a5-4f53-8cb6-393e478b6ec1)

<br/><br/><br/>
> ## Sub Process

### 1) Creating DB
- **ERD Cloud**
![ERD](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/2bda60b3-78fe-48cd-b884-e01fc8876c5f)
<br/><br/><br/>
### 2) Inserting and Selecting Data  
|  | Before INSERT   | After INSERT  |
| :---: | :---: | :---: |
| **다음 경제 뉴스** | 347,759건 | 310,093건 |
| **네이버 경제 뉴스** | 457,817건 | 397,639건 |
| **네이버 뉴스 댓글** | 1,928,758건 | 1,928,758건 |

- **Example of Selecting**
![Select](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/3d5b20b6-a4b7-4ecf-8e88-2821cd60ecb4)
<br/><br/>
---
## 3. Team Members
- 김형석 : hyungsuk0815@gmail.com
- 박수정 : psj0718s@gmail.com
- 손준현 : leonica0429@gmail.com
- 차민경 : chchloe2020@gmail.com
- 팀 notion: [News_Rec_TEAM_4](https://www.notion.so/7d86f33728ae41368121c4b681611519)
---
## 4. References
- [인공지능 기반 추천 시스템 AiRS를 소개합니다.](https://blog.naver.com/naver_diary/220936643956)
- [네이버 뉴스 댓글 크롤링 및 여론 조사 (22.09.13.최신)](https://ukjong.tistory.com/181)
- [[파이썬] Gensim Doc2Vec 모델 생성 및 학습](https://colinch4.github.io/2023-09-06/15-42-26-331788/)
---
## 5. Stacks
<div align='left'>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/MariaDB-003545?style=for-the-badge&logo=mariadb&logoColor=white">
  <img src="https://img.shields.io/badge/Amazon RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white">
  <img src="https://img.shields.io/badge/Visual Studio Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white"/>
  <br>
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white">
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white">
  <img src="https://img.shields.io/badge/Google Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white">
  <img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">
</div>
