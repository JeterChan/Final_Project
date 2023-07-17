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
    M = len(df['Keyword_ID'].unique())

    # Map Ids to indices
    user_mapper = dict(zip(np.unique(df["User_ID"]), list(range(N))))
    keyword_mapper = dict(zip(np.unique(df["Keyword_ID"]), list(range(M))))

    # Map indices to IDs
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["User_ID"])))
    keyword_inv_mapper = dict(zip(list(range(M)), np.unique(df["Keyword_ID"])))

    user_index = [user_mapper[i] for i in df['User_ID']]
    keyword_index = [keyword_mapper[i] for i in df['Keyword_ID']]

    X = csr_matrix((df["Rating"], (keyword_index, user_index)), shape=(M, N))

    return X, user_mapper, keyword_mapper, user_inv_mapper, keyword_inv_mapper

def data_processing(type):

    #讀取使用者評分表 這邊要蓋成用資料庫讀
    ratings = pd.read_excel('data/user_keyword_intersting.xlsx')
    ratings.head()

    """
    #這個是原本模擬資料用的excel檔 新聞的ID是數字 但因為實際新聞ID是字串 所以暫不適用
    keyword = pd.read_excel("data/keyword_all_data.xlsx")
    keyword.head()

    """

    #讀取資料庫內的新聞 目前資料庫假設是keyword.json 
    keyword = pd.DataFrame()
    """
    with open('keyword.json', 'r', encoding='utf-8') as jsonFile:
        f = jsonFile.read()
        a = json.loads(f) 
        df = pd.json_normalize(json.loads(f))
        print(df)
    """
    keyword = pd.read_excel('data/keyword.xlsx')
    keyword.head()

    n_ratings = len(ratings)
    n_keyword = len(ratings['Keyword_ID'].unique())
    n_users = len(ratings['User_ID'].unique())
    """
    print(f"Number of ratings: {n_ratings}")
    print(f"Number of unique Keyword_ID's: {n_keyword}")
    print(f"Number of unique users: {n_users}")
    print(f"Average ratings per user: {round(n_ratings/n_users, 2)}")
    print(f"Average ratings per keyword: {round(n_ratings/n_keyword, 2)}")
    """
    user_freq = ratings[['User_ID', 'Keyword_ID']].groupby('User_ID').count().reset_index()
    user_freq.columns = ['User_ID', 'n_ratings']
    user_freq.head()


    # Find Lowest and Highest rated keywords:
    mean_rating = ratings.groupby('Keyword_ID')[['Rating']].mean()
    # Lowest rated keywords
    lowest_rated = mean_rating['Rating'].idxmin()
    keyword.loc[keyword['Keyword_ID'] == lowest_rated]
    # Highest rated keywords
    highest_rated = mean_rating['Rating'].idxmax()
    keyword.loc[keyword['Keyword_ID'] == highest_rated]
    # show number of people who rated keywords rated keyword highest
    ratings[ratings['Keyword_ID']==highest_rated]
    # show number of people who rated keywords rated keyword lowest
    ratings[ratings['Keyword_ID']==lowest_rated]

    ## the above keywords has very low dataset. We will use bayesian average
    keyword_stats = ratings.groupby('Keyword_ID')[['Rating']].agg(['count', 'mean'])
    keyword_stats.columns = keyword_stats.columns.droplevel()

    # Now, we create user-item matrix using scipy csr matrix
    X, user_mapper, keyword_mapper, user_inv_mapper, keyword_inv_mapper = create_matrix(ratings)

    return X, user_mapper, keyword_mapper, user_inv_mapper, keyword_inv_mapper, keyword, ratings

"""
Find similar keywords using KNN
"""
def find_similar_keywords(keyword_id, X, k, keyword_mapper, keyword_inv_mapper, metric='cosine', show_distance=False):
    neighbour_ids = []
    keyword_ind = keyword_mapper[keyword_id]
    keyword_vec = X[keyword_ind]
    k+=1
    kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
    kNN.fit(X)
    keyword_vec = keyword_vec.reshape(1,-1)
    neighbour = kNN.kneighbors(keyword_vec, return_distance=show_distance)
    for i in range(0,k):
        n = neighbour.item(i)
        neighbour_ids.append(keyword_inv_mapper[n])
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


def find_user_recent_favorite_keyword(user_id):
    ratings = pd.read_excel('data/user_keyword_intersting.xlsx')
    ratings.head()
    user_rating_all= ratings[ratings['User_ID'] == user_id].copy()
    print("這邊是有關於使用者一的資料")
    print(user_rating_all)
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
    keyword_id = random_row.loc[:, 'Keyword_ID'].values[0]
    #print(keyword_id)

    return keyword_id

def find_recommand(keyword_id,type):
    X, user_mapper, keyword_mapper, user_inv_mapper, keyword_inv_mapper, keyword, ratings = data_processing(type)
    all_keyword_titles = dict(zip(keyword['Keyword_ID'], keyword['Keyword_Name']))
    #print("準備要餵入的新聞ID"+str(keyword_id))
    k = 10
    similar_ids = find_similar_keywords(keyword_id, X, k, keyword_mapper, keyword_inv_mapper)
    keyword_titles = all_keyword_titles[keyword_id]
    
    print(f"由於您觀看了 {keyword_titles}")
    print("您會觀看以下新聞\n")

    for i in similar_ids:
        print(all_keyword_titles[i])

    return similar_ids
    
