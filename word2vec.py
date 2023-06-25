import pymongo
from gensim.models import Word2Vec
import logging

myclient = pymongo.MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["News"]


def word2vec(topic,subtopic):

  mycol = mydb[topic]
  # 設定logging
  logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

  # 載入文本數據
  corpus = []
  data = mycol.find({'subtopic': subtopic })
  for document in data:
    corpus.append(document['keyword'])

  print(corpus)
  # 轉換文本數據為tokens列表
  tokens = [sentence.split() for sentence in corpus]

  # 訓練Word2Vec模型
  model = Word2Vec(tokens,vector_size=81,window=5,min_count=1,sg=0,hs=0,negative=10,workers=3,epochs=10,sample=0.05)

  # 儲存模型
  model.save('project_model.model')

  # 加載模型
  loaded_model = Word2Vec.load('project_model.model')

  # 查找相似詞
  similar_words = loaded_model.wv.most_similar("江坤宇", topn=5)
  print(similar_words)

word2vec("運動","中職")