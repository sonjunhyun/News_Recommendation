import pandas as pd

def preprocessing(df):
    df = pd.read_csv('../../daum_economy.csv') #경로설정하여 파일 불러와서 데이터프레임으로 할당
    df.dropna(axis=0, how='any', subset=['title', 'content']) #제목과 본문의 결측치 제거
    df = df[df['content'].apply(lambda x: len(str(x))>50)] #본문 50자 넘는 것만 남기기

    word_list = ['부고', '단신'] 
    text = '|'.join(word_list)
    df = df[~df['title'].str.contains(text)] #부고와 단신 기사 제외
    df = df.reset_index(drop=True) #인덱스 재설정
    return df.to_csv('../../daum_economy_filtered.csv', index=False) 
