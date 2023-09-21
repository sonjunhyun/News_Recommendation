import pandas as pd
from gensim.models.doc2vec import TaggedDocument
from tqdm import tqdm
from gensim.utils import simple_preprocess
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument


# 활용할 데이터 로드하기
def load_data(file_name='total_naver.csv'):
    data = pd.read_csv(f"./{file_name}")
    return data


# 학습 진행
def modeling(data, column_name='content'):
    # 필요한 컬럼만 선택
    docs = data[column_name].tolist()

    # 텍스트 토큰화
    tokenized_docs = [simple_preprocess(doc) for doc in docs]

    # TaggedDocument 객체 생성
    tagged_docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(tokenized_docs)]

    # Doc2Vec 모델 생성
    model = Doc2Vec(vector_size=300, min_count=2, epochs=40, workers=8)

    # 모델 학습
    model.build_vocab(tagged_docs)
    model.train(tagged_docs, total_examples=model.corpus_count, epochs=model.epochs)
    model.save('naver.doc2vec')
    return model


# doc2vec으로 추출된 파일 로드하기
def load_doc2vec(file_name='naver.doc2vec'):
    model = Doc2Vec.load(f'./{file_name}')
    return model


# 유사한 기사 10개 추천 받기
# news_idx = 39000  # 뉴스 index로 입력 -> url이나 제목으로 입력 가능한 기능 추가 고려
# column_list = ['title', 'date_upload', 'content', 'cos_simil'] # 추천받는 기사의 컬럼 선택

def show_similar_results(data, model, news_idx, column_list=['title', 'date_upload', 'content', 'cos_simil']):
    similar_docs = model.dv.most_similar(news_idx)
    result = pd.DataFrame()
    for idx, val in similar_docs:
        temp = data.iloc[[idx]].copy()
        temp.loc[:, 'cos_simil'] = val
        result = pd.concat([result, temp], axis=0)
    return result.loc[:, column_list]