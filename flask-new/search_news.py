#資料庫
from difflib import SequenceMatcher
from pymongo import MongoClient

client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
db_today= client["TodayNews"]
db_daily = client['關鍵每一天']
   
def fuzzy_match(keywords, title):
    keyword_set = set(keywords.split())
    title_set = set(title.split())
    intersection = keyword_set.intersection(title_set)
    similarity = SequenceMatcher(None, keywords, title).ratio()
    return len(intersection), similarity

def search_news(collection_name):
    keywords = db_daily[collection_name].find_one({}, {'keywords': 1})['keywords']  # 提取关键字字段
    news_items = db_today[collection_name].find({}, {'title': 1})  # 提取标题字段

    results = []
    for item in news_items:
        title = item['title']

        total_match_count = 0
        total_similarity = 0

        for keyword in keywords:
            match_count, similarity = fuzzy_match(keyword, title)
            total_match_count += match_count
            total_similarity += similarity

        avg_match_count = total_match_count / len(keywords)
        avg_similarity = total_similarity / len(keywords)

        results.append({'title': title, 'match_count': avg_match_count, 'similarity': avg_similarity})

    # 根据相似度进行排序
    sorted_results = sorted(results, key=lambda x: x['similarity'], reverse=True)

    # 去除重复结果
    unique_results = []
    seen_titles = set()
    for result in sorted_results:
        title = result['title']
        if title not in seen_titles:
            unique_results.append(result)
            seen_titles.add(title)

        # 如果已经找到了10个唯一的结果，提前结束循环
        if len(unique_results) == 20:
            break

    for result in unique_results:
        print(result)

    return unique_results