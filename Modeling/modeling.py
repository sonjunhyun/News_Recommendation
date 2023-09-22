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
    tagged_docs = [TaggedDocument(doc, [i]) for i, doc in zip(data['url'], tokenized_docs)]

    # Doc2Vec 모델 생성
    model = Doc2Vec(vector_size=300, min_count=2, epochs=40, workers=8)

    # 모델 학습
    model.build_vocab(tagged_docs)
    model.train(tagged_docs, total_examples=model.corpus_count, epochs=model.epochs)
    model.save('./test.doc2vec')
    return model


# doc2vec으로 추출된 파일 로드하기
def load_doc2vec(file_name='url_naver.doc2vec'):
    model = Doc2Vec.load(f'./{file_name}')
    return model


# 기사 url 로 유사한 기사 10개 추천받기
def show_similar_results(data, model, url, column_list=['title', 'date_upload', 'content', 'cos_simil']):
    """
    기사 url을 이용해서
    유사한 기사 10개 추천받기
    """
    similar_docs = model.dv.most_similar(url) 
    result = pd.DataFrame()
    for info, val in similar_docs:
        temp = data[data['url'] == info].copy()
        temp.loc[:, 'cos_simil'] = val
        result = pd.concat([result, temp], axis=0)
    return result.loc[:, column_list]