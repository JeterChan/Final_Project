# code
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


import chardet

ratings = pd.read_excel('user_keyword_intersting.xlsx')
ratings.head()

keyword = pd.read_excel("keyword.xlsx")
keyword.head()

n_ratings = len(ratings)
n_keyword = len(ratings['Keyword_ID'].unique())
n_users = len(ratings['User_ID'].unique())

print(f"Number of ratings: {n_ratings}")
print(f"Number of unique keyword_ID's: {n_keyword}")
print(f"Number of unique users: {n_users}")
print(f"Average ratings per user: {round(n_ratings/n_users, 2)}")
print(f"Average ratings per keyword: {round(n_ratings/n_keyword, 2)}")

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
from scipy.sparse import csr_matrix

def create_matrix(df):

    N = len(df['User_ID'].unique())
    M = len(df['Keyword_ID'].unique())

    # Map Ids to indices
    user_mapper = dict(zip(np.unique(df["User_ID"]), list(range(N))))
    keyword_mapper = dict(zip(np.unique(df['Keyword_ID']), list(range(M))))

    # Map indices to IDs
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["User_ID"])))
    keyword_inv_mapper = dict(zip(list(range(M)), np.unique(df['Keyword_ID'])))

    user_index = [user_mapper[i] for i in df['User_ID']]
    keyword_index = [keyword_mapper[i] for i in df['Keyword_ID']]

    X = csr_matrix((df["Rating"], (keyword_index, user_index)), shape=(M, N))

    return X, user_mapper, keyword_mapper, user_inv_mapper, keyword_inv_mapper

X, user_mapper, keyword_mapper, user_inv_mapper, keyword_inv_mapper = create_matrix(ratings)

from sklearn.neighbors import NearestNeighbors
"""
Find similar keywords using KNN
"""
def find_similar_keywords(keyword_id, X, k, metric='cosine', show_distance=False):

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


all_keyword_titles = dict(zip(keyword['Keyword_ID'], keyword['Keyword_Name']))
keyword_id = 96

similar_ids = find_similar_keywords(keyword_id, X, k=10)
keyword_titles = all_keyword_titles[keyword_id]


print(f"由於您將關鍵字 {keyword_titles} 加入最愛")
print("推薦您會喜歡以下關鍵字\n")

for i in similar_ids:
    print(all_keyword_titles[i])