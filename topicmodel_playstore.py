# -*- coding: utf-8 -*-
"""
Created on Mon May 27 10:10:58 2019

Review text import 후 text 내 명사들을 문서단위로 추출합니다.
문서별로 추출된 명사들을 기반으로 특정문서 내의 특정명사가 n번째 토픽에 속할 확률을 학습합니다.
모듈 사용: cmd 혹은 terminal 에서 python topicmodel_playstore.py 리뷰파일이름 토픽수 결과파일이름 을 차례로 입력합니다.
@author: Kyungbin Choi
"""

from konlpy.tag import Okt
import pandas as pd
import sys
from gensim.models import LdaModel
from gensim import corpora
import pyLDAvis.gensim

'''
불용어의 경우 test code 상에서는 임의로 지정했습니다.
추후 stopword list를 지정할 필요가 있습니다.
전체 추출 token중 너무 높은 비중을 차지하는 token도 제외할 필요가 있습니다.
'''
def ldavis(importfile, num_topic, outputfile):
    review_df = pd.read_csv(importfile, encoding='cp949')
    review_df['review_txt'] = review_df['review_txt'].str.replace("\n", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace(r'[0-9]', "")
    review_df['review_txt'] = review_df['review_txt'].str.replace(r'(\.)', "")
    review_df['review_txt'] = review_df['review_txt'].str.replace(r"[ㄱ-ㅎㅏ-ㅣ]+", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace(r"[-=.#/★^&*)~?(:$}]", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace(r"[잼]", "재미")
    review_df['review_txt'] = review_df['review_txt'].str.replace("겜", "게임")
    review_df['review_txt'] = review_df['review_txt'].str.replace("게임", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace("너무", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace("진짜", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace("정말", "")
    review_df['review_txt'] = review_df['review_txt'].str.replace(r"["+str(importfile[:3])+"]+", "")

    # 각 리뷰마다 명사만 남기고 띄어쓰기 기준으로 구분되어 있는 list of list of str
    okt = Okt()
    texts = []
    for i in range(review_df.shape[0]):
        review_noun = [noun_ for noun_ in okt.nouns(review_df.iloc[i, 1]) if len(noun_) > 1]
        texts.append(review_noun)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    NUM_TOPICS = int(num_topic) # This is an assumption.

    ldamodel = LdaModel(
        corpus,
        num_topics=NUM_TOPICS,
        id2word=dictionary,
        passes=20
    )  # This might take some time.
    word_dict = {}

    for i in range(NUM_TOPICS):
        words = ldamodel.show_topic(i, topn=20)
        word_dict['Topic # ' + '{:02d}'.format(i + 1)] = [i[0] for i in words]
    topic_df = pd.DataFrame(word_dict)
    topic_df.to_csv(outputfile+".csv", index=False)

    prepared_data = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
    print("LDA topic modeling ...")
    pyLDAvis.save_html(prepared_data, outputfile+".html")

def main(argv):
    if len(sys.argv) != 4:
        print("python 모듈이름 importfile number_of_topics outputfile")
    importfile = sys.argv[1]
    num_of_topics = sys.argv[2]
    outputfile = sys.argv[3]
    ldavis(importfile, num_of_topics, outputfile)

if __name__ == '__main__':
    main(sys.argv)