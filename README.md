# 컨텐츠 기반 필터링(Doc2Vec)을 이용한 경제 뉴스 기사 추천 시스템 만들기
## 1. Outline
![Outline](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/5260fe83-6b91-402d-84e1-ad40fbbee88e)

## 2. Period & Process
![process](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/73fe9ed9-c3f3-4555-ae11-9d7f8118445e)

### 1) Main Process

#### Project Plan


**① [다음 경제 뉴스 기사](https://news.daum.net/breakingnews/economic)**

- 수집기간 : 2023년 06월 13일 ~ 2023년 09월 13일 (3개월)
- 소분류 : 금융, 기업산업, 취업직장인, 경제일반, 자동차, 주식, 시황분석, 공시, 해외증시, 채권선물, 외환, 주식일반, 부동산, 생활경제, 국제경제
- 수집내용 : 제목, 기자, 언론사, 본문, 작성일자, 수정일자, 스티커, url
- 기사 347,759건

**② [네이버 경제 뉴스 기사](https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101)**

- 수집기간 : 2023년 06월 13일 ~ 2023년 09월 13일 (3개월)
- 소분류 : 금융, 증권, 산업/재계, 중기/벤처, 부동산, 글로벌 경제, 생활경제, 경제 일반
- 수집내용 : 제목, 기자, 언론사, 본문, 작성일자, 수정일자, 스티커, url, 댓글(유저 id, 유저 닉네임, 작성일자, 좋아요 수, 싫어요 수)
- 기사 457,817건,  댓글 1,928,758건
---

#### Pre-processing

- 날짜 형식의 컬럼은 datetime 형식으로 변환, 네이버&다음 날짜 형식 통일
- 제목(title) 또는 본문(content)이 결측치인 row 제거
- 본문 글자 수가 50자 미만인 row 제거
- 제목에 '부고'와 '단신'과 같은 경제와 직접적인 연관이 없는 키워드를 포함하는 row 제거
---
#### Modelling - Using Gensim Library

![gensim](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/1e053994-9d80-4028-ba7e-a7339f1b98d1)

- 자연어를 벡터로 변환하는 데 필요한 편의 기능을 제공하는 라이브러리
- Word2Vec, Doc2Vec 함수 포함
- 뉴스 본문 tokenization (simple_preprocess)
- TaggedDocument 생성 → Doc2Vec 모델 생성 및 학습
---
#### Using Recommendation System

- 기사 url 입력 → 본문과 유사한 뉴스 10개 추천

![url](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/977f7471-2071-4250-9818-39aa2fffd379)


![recommend](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/a95e99f1-a4a5-4f53-8cb6-393e478b6ec1)

---
### 2) Sub Process

#### Building DB
- **ERD Cloud**
![ERD](https://github.com/sesac-2023/FINANCIAL_NEWS_TEAM_4/assets/76051357/2bda60b3-78fe-48cd-b884-e01fc8876c5f)


