# 導入 模組(module) 
import requests 
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from gensim.models import Word2Vec
import jieba
import mysql.connector



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


def find_most_similar_title(summary, titles):
    print("符合的PTT標題如下：")
    count_list = []
    # 使用jieba進行分詞
    for title in titles:
        count = 0
        seg_list = jieba.cut(title)
        # 將分詞結果存入陣列
        word_list = []
        for word in seg_list:
            word_list.append(word)    
        for word in word_list:
            if word in summary:
                count += 1
        if(count>3):
            count_list.append([title,count])
            print(title)


current_dir = os.getcwd()
driver_name = "chromedriver.exe"
driver_path = current_dir+"\\"+driver_name


def open_ptt_url_fillter_subtopic(sub_topic):

    host = 'localhost'
    user = '你的資料庫使用者'
    password = '你的資料庫密碼'
    database = '你的資料庫名稱'
    charset =  "utf8"
    
    connection = mysql.connector.connect(host=host, user=user, password=password, database=database, charset=charset)
    
    cursor = connection.cursor()
    # SQL查询语句
    select_query = "SELECT * FROM tb_ptt_search_link"
    # 执行查询
    cursor.execute(select_query)
    # 获取所有结果
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
    print(df)

    filtered_df = df[df['subtopic'] == sub_topic]

    #return filtered_df

open_ptt_url_fillter_subtopic("棒球")


def fillter_user_keyword(df,user_keyword):
    filtered_df = df[df['Title'].str.contains(user_keyword)]

    return filtered_df

def time_sort(df):
    df_sorted = df.sort_values(by='Index', ascending=False)

    return df_sorted

def edit_distance(str1, str2):
    m = len(str1)
    n = len(str2)
    
    # 创建一个二维数组来存储编辑距离
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # 初始化第一行和第一列
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # 动态规划计算编辑距离
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],       # 删除操作
                                   dp[i][j - 1],       # 插入操作
                                   dp[i - 1][j - 1])   # 替换操作
                
    return dp[m][n]

def compute_similarity(df_ptt,news_list):
    
    ptt_title_list = [] #[['新聞一的ptt1','新聞一的ptt2','新聞一的ptt3'],['新聞二的ptt1','新聞二的ptt2','新聞二的ptt3']]
    ptt_link_list = []
    ptt_list = df_ptt['Title'].tolist()

    for yahoo_news_summary in news_list:
        temp_ptt_title_list = []
        temp_ptt_link_list = []
        print("進入PTT篩選的摘要如下："+yahoo_news_summary[0])
        most_similar_title = find_most_similar_title(yahoo_news_summary[0], ptt_list)
        print("相似度最高的標題：", most_similar_title,"\n")

    return ptt_title_list


def choose_ptt_data(news_list,user_keyword,user_subtopic):
    print(news_list)
    df_ptt = open_ptt_url_fillter_subtopic(user_subtopic)
    df_ptt = fillter_user_keyword(df_ptt,user_keyword)
    df_ptt = time_sort(df_ptt)
    df_ptt = compute_similarity(df_ptt,news_list)


    return df_ptt
    
