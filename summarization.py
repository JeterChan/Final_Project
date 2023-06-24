import pymongo
import requests
import jieba
import numpy as np
import collections
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer  
import requests
from bs4 import BeautifulSoup
import re

def split_sentence(text, punctuation_list=r'!?。！？"'):  #按標點分割句子
    sentence_set = []
    inx_position = 0
    char_position = 0
    for char in text:
        char_position += 1
        if char in punctuation_list:
            next_char = list(text[inx_position:char_position+1]).pop()
            if next_char not in punctuation_list:
                sentence_set.append(text[inx_position:char_position])
                inx_position = char_position
    if inx_position < len(text):
        sentence_set.append(text[inx_position:])
    sentence_with_index = {i:sent for i,sent in enumerate(sentence_set)}
    return sentence_set,sentence_with_index

def get_tfidf_matrix(sentence_set,stop_word):  #移除停用詞並轉換為矩陣
    corpus = []
    for sent in sentence_set:
        sent_cut = jieba.cut(sent, cut_all=False)
        sent_list = [word for word in sent_cut if word not in stop_word]
        sent_str = ' '.join(sent_list)
        corpus.append(sent_str)
    vectorizer=CountVectorizer()
    transformer=TfidfTransformer()
    tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))
    tfidf_matrix=tfidf.toarray()
    return np.array(tfidf_matrix)

def get_sentence_with_words_weight(tfidf_matrix):  #計算句子權重
    sentence_with_words_weight = {}
    for i in range(len(tfidf_matrix)):
        sentence_with_words_weight[i] = np.sum(tfidf_matrix[i])
    max_weight = max(sentence_with_words_weight.values()) #归一化
    min_weight = min(sentence_with_words_weight.values())
    for key in sentence_with_words_weight.keys():
        x = sentence_with_words_weight[key]
        sentence_with_words_weight[key] = (x-min_weight)/(max_weight-min_weight)
    return sentence_with_words_weight

def get_sentence_with_position_weight(sentence_set):  #計算位置權重
    sentence_with_position_weight = {}
    total_sent = len(sentence_set)
    for i in range(total_sent):
        sentence_with_position_weight[i] = (total_sent - i) / total_sent
    return sentence_with_position_weight

def similarity(sent1,sent2):  #計算兩句子相似度
    return np.sum(sent1 * sent2) / 1e-6+(np.sqrt(np.sum(sent1 * sent1)) * np.sqrt(np.sum(sent2 * sent2)))

def get_similarity_weight(tfidf_matrix):  #計算相似度權重
    sentence_score = collections.defaultdict(lambda :0.)
    for i in range(len(tfidf_matrix)):
        score_i = 0.
        for j in range(len(tfidf_matrix)):
            score_i += similarity(tfidf_matrix[i],tfidf_matrix[j])
        sentence_score[i] = score_i
    max_score = max(sentence_score.values()) #归一化
    min_score = min(sentence_score.values())
    for key in sentence_score.keys():
        x = sentence_score[key]
        sentence_score[key] = (x-min_score)/(max_score-min_score)
    return sentence_score

def ranking_base_on_weigth(sentence_with_words_weight,  #按句子權重排序
                            sentence_with_position_weight,
                            sentence_score, feature_weight):
    sentence_weight = collections.defaultdict(lambda :0.)
    for sent in sentence_score.keys():
        sentence_weight[sent] = feature_weight[0]*sentence_with_words_weight[sent] +\
                                feature_weight[1]*sentence_with_position_weight[sent] +\
                                feature_weight[2]*sentence_score[sent]
    sort_sent_weight = sorted(sentence_weight.items(),key=lambda d: d[1], reverse=True)
    return sort_sent_weight

def get_summarization(sentence_with_index,sort_sent_weight,topK_ratio):  #取得摘要
    topK = int(len(sort_sent_weight)*topK_ratio)
    summarization_sent = sorted([sent[0] for sent in sort_sent_weight[:topK]])
    summarization = []
    for i in summarization_sent:
        summarization.append(sentence_with_index[i])
    summary = ''.join(summarization)

     # 檢查摘要是否為空白，如果是則提高 topK_ratio 值並重新生成摘要
    if summary.strip() == '':
        topK_ratio += 0.05
        return get_summarization(sentence_with_index ,sort_sent_weight, topK_ratio)
    
    chars_to_remove = r" -」)_!?。！？'）】.%"  # 要刪除的字元
    processed_summary = summary.lstrip(chars_to_remove)
    return processed_summary  

def get_content(url):

    response = requests.get(url)
     # 检查响应的状态码
    if response.status_code == 404:
        text_content="404"
    else:
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        caas_body = soup.find('div', class_='caas-body')  # 選取class為'caas-body'的<div>元素
        paragraphs = caas_body.find_all('p')  # 在選取的<div>元素中尋找所有<p>標籤

        # 使用正則表達式去除贅字    #【記者 王苡蘋╱高雄 報導】                        #【記者陳雅芳／彰化報導】                        #（記者王乙徹／台中報導）                        #鄉民中心／李育道報導                          #記者陳金龍∕南投報導                        #娛樂中心/洪雨汝 報導
        pattern_A = re.compile(r'(\【+[^\s]*\s*[^\s]*\s*\╱+\s*[^\s]*\s*報導\】)|([^\s]*\s*[^\s]+\s*\／+\s*[^\s]*\s*報導\】)|([^\s]*\s*[^\s]*\s*\／+\s*[^\s]*\s*報導\）)|([^\s]*\s*[^\s]*\s*\／+\s*[^\s]*\s*報導)|([^\s]*\s*[^\s]*\s*\∕+\s*[^\s]*\s*報導)|([^\s]*\s*[^\s]*\s*\/+\s*[^\s]*\s*報導)')
                                #[NOWnews今日新聞]           #（中央社記者劉冠廷台北23日電）     #（路透巴黎23日電）              #（觀傳媒新北新聞）                 #[Newtalk新聞]              #【健康醫療網／編輯部整理】
        pattern_B= re.compile(r'(\[+\s*NOWnews今日新聞+\s*\])|(\（+\s*中央社+\s*[^\s]*\s*\）)|(\（+\s*路透+\s*[^\s]*\s*\）)|(\（+\s*觀傳媒+\s*[^\s]*\s*\）)|(\[+\s*Newtalk新聞+\s*\])|(\【健康醫療網\／編輯部整理\】)')
                                # 匹配「更多」後面的任意字元（包括換行符號）直到行尾 
                                            #更多民視新聞報導 #更多 NOWnews 今日新聞 報導 #更多 TVBS 報導                                  #看更多 CTWANT 文章
        pattern_C = re.compile(r'(延伸閱讀.*$)|(查看原文.*$)|(原始連結.*$)|(更多+\s*[^\s]*\s*[^\s]*報導.*$)|(更多+\s*[^\s]*\s*[^\s]*新聞.*$)|(看更多+\s*[^\s]*\s*[^\s]*文章.*$)')  
        text_content = ' '.join([(pattern_C.sub('',pattern_B.sub('', pattern_A.sub('', p.get_text())))) for p in paragraphs])

    return text_content

# 停用詞
stops = []
with open('專題\stopWord_summar.txt', 'r', encoding='utf-8-sig') as f:
    for line in f.readlines():
        stops.append(line.strip())

myclient = pymongo.MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["News"]

topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]#
for topic in topics:
    mycol = mydb[topic]
    for document in mycol.find():
        url = document['url']
        content=get_content(url)
        sentences, indexs =split_sentence(content)          # 按標點分割句子
        tfidf = get_tfidf_matrix(sentences, stops)             # 移除停用詞並轉換為矩陣
        word_weight =get_sentence_with_words_weight(tfidf)    # 計算句子關鍵詞權重
        posi_weight = get_sentence_with_position_weight(sentences)     # 計算位置權重
        scores = get_similarity_weight(tfidf)                  # 計算相似度權重
        sort_weight = ranking_base_on_weigth(word_weight, posi_weight, scores, feature_weight=[3,0,2])
        summary = get_summarization(indexs ,sort_weight, topK_ratio=0.2) # 取得摘要比例
        # 更新資料庫的每一筆記錄
        mycol.update_one({"_id": document["_id"]}, {"$set": {"content": content, "summary": summary}})
        #在正式存資料庫之前先檢查一下有沒有對
        #print("id:")
        #print(document["_id"])
        #print("content:")
        #print(content)
        #print("summary:")
        #print(summary)














