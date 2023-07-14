# code
import json
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns

import warnings

import chardet
from datetime import datetime,timedelta

from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

warnings.simplefilter(action='ignore', category=FutureWarning)

def create_matrix(df):

    N = len(df['User_ID'].unique())
    M = len(df['News_ID'].unique())

    # Map Ids to indices
    user_mapper = dict(zip(np.unique(df["User_ID"]), list(range(N))))
    news_mapper = dict(zip(np.unique(df["News_ID"]), list(range(M))))

    # Map indices to IDs
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["User_ID"])))
    news_inv_mapper = dict(zip(list(range(M)), np.unique(df["News_ID"])))

    user_index = [user_mapper[i] for i in df['User_ID']]
    news_index = [news_mapper[i] for i in df['News_ID']]

    X = csr_matrix((df["Rating"], (news_index, user_index)), shape=(M, N))

    return X, user_mapper, news_mapper, user_inv_mapper, news_inv_mapper

def data_processing(type):

    #讀取使用者評分表 這邊要蓋成用資料庫讀
    ratings = pd.read_excel('data/user_news_rating.xlsx')
    ratings.head()

    """
    #這個是原本模擬資料用的excel檔 新聞的ID是數字 但因為實際新聞ID是字串 所以暫不適用
    news = pd.read_excel("data/news_all_data.xlsx")
    news.head()

    """


    #讀取資料庫內的新聞 目前資料庫假設是news.json 
    news = pd.DataFrame()
    with open('news.json', 'r', encoding='utf-8') as jsonFile:
        f = jsonFile.read()
        a = json.loads(f) 
        df = pd.json_normalize(json.loads(f))
        print(df)

        subset_df = df[['_id.$oid','title','topic']]

        # 打印合并后的DataFrame
        print(subset_df)

        subset_df = subset_df.rename(columns={'_id.$oid': 'News_ID'})
        subset_df = subset_df.rename(columns={'title': 'Title'})
        news = subset_df
        # 打印子集DataFrame
        #print(subset_df)


    n_ratings = len(ratings)
    n_news = len(ratings['News_ID'].unique())
    n_users = len(ratings['User_ID'].unique())
    """
    print(f"Number of ratings: {n_ratings}")
    print(f"Number of unique News_ID's: {n_news}")
    print(f"Number of unique users: {n_users}")
    print(f"Average ratings per user: {round(n_ratings/n_users, 2)}")
    print(f"Average ratings per news: {round(n_ratings/n_news, 2)}")
    """
    user_freq = ratings[['User_ID', 'News_ID']].groupby('User_ID').count().reset_index()
    user_freq.columns = ['User_ID', 'n_ratings']
    user_freq.head()


    # Find Lowest and Highest rated newss:
    mean_rating = ratings.groupby('News_ID')[['Rating']].mean()
    # Lowest rated newss
    lowest_rated = mean_rating['Rating'].idxmin()
    news.loc[news['News_ID'] == lowest_rated]
    # Highest rated newss
    highest_rated = mean_rating['Rating'].idxmax()
    news.loc[news['News_ID'] == highest_rated]
    # show number of people who rated newss rated news highest
    ratings[ratings['News_ID']==highest_rated]
    # show number of people who rated newss rated news lowest
    ratings[ratings['News_ID']==lowest_rated]

    ## the above newss has very low dataset. We will use bayesian average
    news_stats = ratings.groupby('News_ID')[['Rating']].agg(['count', 'mean'])
    news_stats.columns = news_stats.columns.droplevel()

    # Now, we create user-item matrix using scipy csr matrix
    X, user_mapper, news_mapper, user_inv_mapper, news_inv_mapper = create_matrix(ratings)

    return X, user_mapper, news_mapper, user_inv_mapper, news_inv_mapper, news, ratings

"""
Find similar newss using KNN
"""
def find_similar_newss(news_id, X, k, news_mapper, news_inv_mapper, metric='cosine', show_distance=False):
    neighbour_ids = []
    news_ind = news_mapper[news_id]
    news_vec = X[news_ind]
    k+=1
    kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
    kNN.fit(X)
    news_vec = news_vec.reshape(1,-1)
    neighbour = kNN.kneighbors(news_vec, return_distance=show_distance)
    for i in range(0,k):
        n = neighbour.item(i)
        neighbour_ids.append(news_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids

def generate_today_date():
    # 獲取當前日期和時間
    now = datetime.now()

    # 將日期轉換為指定格式
    date_string = now.strftime("%Y%m%d")
    return date_string

def generate_previos_date(version):
    if version == "one_week_ago":
        now = datetime.now()
        # 將日期轉換為指定格式
        one_week_ago = now - timedelta(days=7)
        date_string = now.strftime("%Y%m%d")

    if version == "one_month_ago":
        now = datetime.now()
        # 將日期轉換為指定格式
        one_month_ago = now - timedelta(days=30)
        date_string = one_month_ago.strftime("%Y%m%d")
    
    return date_string


def find_user_recent_score_news(user_id):
    ratings = pd.read_excel('data/user_news_rating.xlsx')
    ratings.head()
    user_rating_all= ratings[ratings['User_ID'] == user_id].copy()
    today_date = generate_today_date()
    previous_date = generate_previos_date("one_week_ago")
    user_rating_near = user_rating_all[user_rating_all['Date']>=int(previous_date)]
    if user_rating_near.empty:
        previous_date = generate_previos_date("one_month_ago")
        user_rating_near = user_rating_all[user_rating_all['Date']>=int(previous_date)]
        #如果再沒有，就從最近一個觀看的新聞抓取
    #print(user_rating_near)
    grestest_user_rating_near = user_rating_near[user_rating_near['Rating'] >= 9]
    if grestest_user_rating_near.empty:
        grestest_user_rating_near = user_rating_near[user_rating_near['Rating'] >= 6]
        #如果再沒有，
    #print(grestest_user_rating_near)
    random_row = grestest_user_rating_near.sample(n=1)
    # 輸出隨機選擇的資料
    news_id = random_row.loc[:, 'News_ID'].values[0]
    #print(news_id)

    return news_id

def find_recommand(news_id,type):
    X, user_mapper, news_mapper, user_inv_mapper, news_inv_mapper, news, ratings = data_processing(type)
    all_news_titles = dict(zip(news['News_ID'], news['Title']))
    #print("準備要餵入的新聞ID"+str(news_id))
    k = 10
    similar_ids = find_similar_newss(news_id, X, k, news_mapper, news_inv_mapper)
    news_titles = all_news_titles[news_id]

    
    print(f"由於您觀看了 {news_titles}")
    print("您會觀看以下新聞\n")

    for i in similar_ids:
        print(all_news_titles[i])

    return similar_ids
    
