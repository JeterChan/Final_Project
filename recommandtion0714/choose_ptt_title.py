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

current_dir = os.getcwd()
driver_name = "chromedriver.exe"
driver_path = current_dir+"\\"+driver_name


def open_ptt_url_fillter_subtopic(sub_topic):
    ptt_data = 'data/ptt_all_data.xlsx'
    df = pd.read_excel(ptt_data)
    filtered_df = df[df['Sub_Topic'] == sub_topic]

    return filtered_df

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

def compute_distance(df_ptt,yahoo_news):
    
    ptt_title_list = [] #[['新聞一的ptt1','新聞一的ptt2','新聞一的ptt3'],['新聞二的ptt1','新聞二的ptt2','新聞二的ptt3']]
    ptt_link_list = []

    for yahoo_news_summary in yahoo_news:
        temp_ptt_title_list = []
        temp_ptt_link_list = []
        for index, row in df_ptt.iterrows():
            ptt_community_title = row['Title']
            ptt_community_link = row['Link']
            distance = edit_distance(ptt_community_title, yahoo_news_summary)
            if distance < 200:
                temp_ptt_title_list.append(ptt_community_title)
                temp_ptt_link_list.append(ptt_community_link)

            if len(temp_ptt_title_list) == 3 or index==len(df_ptt)-1:
                ptt_title_list.append(temp_ptt_title_list)
                ptt_link_list.append(temp_ptt_link_list)
                break

    return ptt_title_list


def choose_ptt_data(news_list,user_keyword,user_subtopic):
    df_ptt = open_ptt_url_fillter_subtopic(user_subtopic)
    df_ptt = fillter_user_keyword(df_ptt,user_keyword)
    df_ptt = time_sort(df_ptt)
    df_ptt = compute_distance(df_ptt,news_list)

    return df_ptt
    
