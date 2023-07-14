# -*- coding: utf-8 -*-
import jieba
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
import random
import pandas as pd
import os

current_dir = os.getcwd()

data_documentary_name = "data"
data_path = current_dir+"\\"+data_documentary_name+"\\"

stopwords_name = "stop_words.txt"
stopwords_path = data_path+stopwords_name

CLSTER_NUM = 50

class KmeansClustering():
    def __init__(self, stopwords_path=stopwords_path):
        self.stopwords = self.load_stopwords(stopwords_path)
        self.vectorizer = CountVectorizer()
        self.transformer = TfidfTransformer()

    def load_stopwords(self, stopwords=None):
        """
        加载停用词
        :param stopwords:
        :return:
        """
        if stopwords:
            with open(stopwords, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f]
        else:
            return []

    def preprocess_data(self,corpus_path):
        """
        文本预处理，每行一个文本
        :param corpus_path:
        :return:
        """
        
        corpus = []
        
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                corpus.append(' '.join([word for word in jieba.lcut(line.strip()) if word not in self.stopwords]))
        
        return corpus
        

    def get_text_tfidf_matrix(self, corpus):
        """
        获取tfidf矩阵
        :param corpus:
        :return:
        """
        tfidf = self.transformer.fit_transform(self.vectorizer.fit_transform(corpus))

        # 获取词袋中所有词语
        # words = self.vectorizer.get_feature_names()

        # 获取tfidf矩阵中权重
        weights = tfidf.toarray()
        return weights

    def kmeans(self, corpus_path, n_clusters=CLSTER_NUM):
        """
        KMeans文本聚类
        :param corpus_path: 语料路径（每行一篇）,文章id从0开始
        :param n_clusters: ：聚类类别数目
        :return: {cluster_id1:[text_id1, text_id2]}
        """
        corpus = self.preprocess_data(corpus_path)
        weights = self.get_text_tfidf_matrix(corpus)

        clf = KMeans(n_clusters=n_clusters)

        # clf.fit(weights)

        y = clf.fit_predict(weights)

        # 中心点
        # centers = clf.cluster_centers_

        # 用来评估簇的个数是否合适,距离约小说明簇分得越好,选取临界点的簇的个数
        # score = clf.inertia_

        # 每个样本所属的簇
        result = {}
        for text_idx, label_idx in enumerate(y):
            key = "cluster_{}".format(label_idx)
            if key not in result:
                result[key] = [text_idx]
            else:
                result[key].append(text_idx)
        return result

def choose_final_news(result,df_news,cluster_num): #result是kmeans的結果
    print("這是result")
    print(result)
    final_news_index = []
    final_news_title = []
    for i in range(cluster_num):
        cluster = "cluster_"+str(i)
        cluster_content = result[cluster]
        #print(cluster_content)
        random_number = random.randint(0, len(cluster_content)-1)  # 產生範圍在0到n-1之間的隨機整數
        #print(random_number)
        final_news_index.append(cluster_content[random_number])
    
    return final_news_index

def translate_text_to_dataframe(file):
    file = data_path+file
    df = pd.read_csv(file, delimiter='\t', header=None)
    return df


def run_kmeans(news_summary,cluster_num):
    
    with open(data_path+'kmeans.txt', "w",encoding='utf-8') as file:
        # 遍历列表，逐行写入文件
        for item in news_summary:
            file.write(item+"\n")
    CLSTER_NUM = cluster_num

    Kmeans = KmeansClustering(stopwords_path=stopwords_path)
    result = Kmeans.kmeans(data_path+'kmeans.txt', n_clusters=cluster_num)
    
    df_news_summary = translate_text_to_dataframe('kmeans.txt')

    output_news_list = choose_final_news(result,df_news_summary,cluster_num)
    finished_kmeans_summary = []

    for news_index in (output_news_list):
        finished_kmeans_summary.append(news_summary[news_index])
    return finished_kmeans_summary

