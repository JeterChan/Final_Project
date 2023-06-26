# code
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


import chardet

ratings = pd.read_excel('rating.xlsx')
ratings.head()

news = pd.read_excel("news_all_data.xlsx")
news.head()

n_ratings = len(ratings)
n_news = len(ratings['News_ID'].unique())
n_users = len(ratings['User_ID'].unique())

print(f"Number of ratings: {n_ratings}")
print(f"Number of unique News_ID's: {n_news}")
print(f"Number of unique users: {n_users}")
print(f"Average ratings per user: {round(n_ratings/n_users, 2)}")
print(f"Average ratings per news: {round(n_ratings/n_news, 2)}")

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
from scipy.sparse import csr_matrix

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

X, user_mapper, news_mapper, user_inv_mapper, news_inv_mapper = create_matrix(ratings)

from sklearn.neighbors import NearestNeighbors
"""
Find similar newss using KNN
"""
def find_similar_newss(news_id, X, k, metric='cosine', show_distance=False):

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


all_news_titles = dict(zip(news['News_ID'], news['Title']))
news_id = 130

similar_ids = find_similar_newss(news_id, X, k=10)
news_titles = all_news_titles[news_id]


print(f"由於您觀看了 {news_titles}")
print("您會觀看以下新聞\n")

for i in similar_ids:
    print(all_news_titles[i])