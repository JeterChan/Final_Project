from gensim.models import Word2Vec


def train(corpus):
    tokens = [sentence.split() for sentence in corpus]

    # 訓練Word2Vec模型
    model = Word2Vec(tokens,vector_size=100,window=10,min_count=20,sg=0,hs=1,negative=10,workers=1,epochs=20,sample=1e-3)

    # 儲存模型
    model.save('project_model_v1.model')  


def word2vec(kw):
  try:
    loaded_model = Word2Vec.load('project_model_v1.model')
    similar_words = loaded_model.wv.most_similar(kw, topn=5)
    filtered_words = [word for word, score in similar_words if score > 0.5]
  except KeyError:
    filtered_words = "None"
  return filtered_words

