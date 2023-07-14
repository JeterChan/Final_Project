#這邊是登入後搜尋的頁面流程
import sys

import re
import  math
import json
import pandas as pd
from json import load

import kmeans
import recommand_by_news_rating 
#import recommand_by_
import choose_ptt_title

user_id = 1
user_search = "大谷"

#這一邊給網頁讀取user是誰

##############
##          ##
##          ##
##          ##
##          ##
##############

#找出與user_search 相關的延伸關鍵字 ex:棒球、

##############
##          ##
##          ##
##          ##
##          ##
##############


#將延伸關鍵字與協同過濾的使用者最愛關鍵字列表配對
#選擇一個與使用者搜尋最相關且有位於使用者最愛關鍵字列表配對的關鍵字


#將此關鍵字拿去做偕同過濾
#input：關鍵字 (string)
#output：協同過濾的推薦關鍵字 (string list)

##將關鍵字協同過濾的結果與關鍵字延伸的結果進行比對，如果有配對到，則優先輸出


#前半部為關鍵字處理
#==========================================================================#
#後半部為新聞、ptt處理

#讀取資料庫資料，目前資料庫假設是news.json 
news_summary_list = []
news_id_list = []
with open('news.json', 'r', encoding='utf-8') as jsonFile:
    f = jsonFile.read()
    a = json.loads(f) 
    df = pd.json_normalize(json.loads(f))

    # 提取'id'字段的值并存储在列表中
    news_summary_list = df['summary'].tolist()
    news_id_list = df['_id.$oid'].tolist()
    


#篩選第一輪字串比對完的新聞
# input：所有資料庫的新聞
# output：字串比對完符合的新聞
string_filtered_newslist =  [value for value in news_summary_list if user_search in value]

print(len(string_filtered_newslist))

#資料庫中完全沒有相關的新聞
if len(string_filtered_newslist)==0: #如果完全沒有相關新聞，則在網頁輸出無相關新聞
    print("沒有相關的新聞")
    sys.exit()

#進行k-means 將相同性質的移除
#input：字串比對完的新聞 (list)
#output：k-means完的50篇新聞 (list)

kmeans_filtered_newslist_id = []


if len(string_filtered_newslist)>=0 and len(string_filtered_newslist)<=50:
    finished_kmens_summary_list = kmeans.run_kmeans(string_filtered_newslist,math.ceil(len(string_filtered_newslist)/2))

if len(string_filtered_newslist)>50:
    finished_kmens_summary_list = kmeans.run_kmeans(string_filtered_newslist,50)


#這邊的id是fillter過的新聞裡面的id(資料型態為int)，要變為原本資料庫的id(資料型態為string)，以便後續跟偕同過濾比對

kmeans_original_id_list = []
for summary in finished_kmens_summary_list:
    kmeans_original_id_list.append(df.loc[df['summary'] == summary , '_id.$oid'].tolist())

#進行協同過濾 將推薦新聞優先推薦給使用者
#input：user id (int)
#output：推薦的新聞 (list)
news_id = recommand_by_news_rating.find_user_recent_score_news(user_id)  #將過濾出來的50篇新聞 與使用者最近一星期評分最高的新聞做偕同過濾 分數高的新聞會優先輸出。
collabrative_original_id_list = recommand_by_news_rating.find_recommand(news_id,"from_all_news")


#將協同過濾的結果與k-means的結果進行比對，如果有配對到，則優先輸出
#input：k-means完的50篇新聞,協同過濾完的50篇新聞
#output：有成功配對到需要優先輸出的新聞

pair_id_list = []
print("這邊是主程式的kmeans")
print(kmeans_original_id_list)

for collabrative_id in collabrative_original_id_list:
    for kmeans_id in kmeans_original_id_list:
        if kmeans_id == collabrative_id:
            pair_id_list.append(kmeans_id)
            break

output_id_list = pair_id_list + [x for x in kmeans_original_id_list if x not in pair_id_list]

# output_id_list為需要輸出新聞ID列表
print("輸出的ID(已按照排序)")
print(output_id_list)


#找PTT相關的留言
#input：需要回傳到網站的新聞摘要 (list), 主題, hashtag
#output：其新聞相關之社群留言 (二維list) [['新聞一的ptt'],[]]


sub_topic = df.loc[df['summary'] == finished_kmens_summary_list[0], 'subtopic'].values[0]
print(sub_topic)

#print(finished_kmens_summary_list)
ptt_output_list = choose_ptt_title.choose_ptt_data(finished_kmens_summary_list,user_search,sub_topic)
print(ptt_output_list)





