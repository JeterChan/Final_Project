#資料庫
from difflib import SequenceMatcher
from pymongo import MongoClient

client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")

db_all= client["News"]
db_today= client["TodayNews"]
db_daily = client['關鍵每一天']
total_subject = ['健康', '國際', '娛樂', '生活', '社會地方', '科技', '財經', '運動']
def fuzzy_match(keywords, title):
    keyword_set = set(keywords.split())
    title_set = set(title.split())
    intersection = keyword_set.intersection(title_set)
    similarity = SequenceMatcher(None, keywords, title).ratio()
    return len(intersection), similarity

def hot_topic_search_news(collection_name):
    keywords = db_daily[collection_name].find_one({}, {'keywords': 1})['keywords']  # 提取关键字字段
    news_items = db_today[collection_name].find({}, {'title': 1,'url':1,'image':1,'summary':1})  # 提取标题字段

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

        results.append({'title': title,'url': item['url'] ,'image':item['image'],'summary':item['summary'],'match_count': avg_match_count, 'similarity': avg_similarity})

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

    #for result in unique_results:
        #print(result)

    return unique_results

def search_total_news(all_keywords,num):
    selected_news = []  # 存储最相似的新闻

    for collection_name in total_subject:
        # 聚合查询，筛选出包含关键字的新闻并计算相似度
        pipeline = [
        {
            '$match': {
                '$or': [
                    {'title': {'$regex': f'.*{kw}.*', '$options': 'i'}} for kw in all_keywords
                ]
            }
        },
        {
            '$addFields': {
                'combined_text': {'$concat': ['$title', ' ', '$content']}
            }
        },
        {
            '$project': {
                '_id': 0,
                'title': 1,
                'url': 1,
                'image': 1,
                'content': 1,
                'summary': 1,
                'match_count': {
                    '$size': {
                        '$setIntersection': [
                            {'$split': ['$combined_text', ' ']},
                            all_keywords
                        ]
                    }
                },
                'similarity': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$gt': [{'$size': {'$split': ['$combined_text', ' ']}} , 0]},
                                {'$ne': ['$combined_text', None]}
                            ]
                        },
                        'then': {
                            '$divide': [
                                {'$ifNull': ['$match_count', 0]},
                                {'$size': {'$split': ['$combined_text', ' ']}}
                            ]
                        },
                        'else': 0
                    }
                }
            }
        },
        {
            '$sort': {'similarity': -1, 'timestamp': -1}
        },
        {
            '$limit': num
        }
        ]

        news_data = list(db_today[collection_name].aggregate(pipeline))

        # 将结果添加到 selected_news 列表中
        selected_news.extend(news_data)


    # 将全部主题的新闻按照相似度排序
    selected_news.sort(key=lambda x: x['similarity'], reverse=True)
    # 仅保留前4个结果
    selected_news = selected_news[:4]

    return selected_news

def gen_kw_search_news(keyword,num):
    selected_news = []  # 存储最相似的新闻

    for collection_name in total_subject:
        # 聚合查询，筛选出包含关键字的新闻并计算相似度
        pipeline = [
        {
            '$match': {
                '$or': [
                    {'title': {'$regex': f'.*{keyword}.*', '$options': 'i'}}
                ]
            }
        },
        {
            '$addFields': {
                'combined_text': {'$concat': ['$title', ' ', '$content']}
            }
        },
        {
            '$project': {
                '_id': 0,
                'title': 1,
                'url': 1,
                'image': 1,
                'content': 1,
                'summary': 1,
                'match_count': {
                    '$size': {
                        '$setIntersection': [
                            {'$split': ['$combined_text', ' ']},
                            keyword
                        ]
                    }
                },
                'similarity': {
                    '$cond': {
                        'if': {
                            '$and': [
                                {'$gt': [{'$size': {'$split': ['$combined_text', ' ']}} , 0]},
                                {'$ne': ['$combined_text', None]}
                            ]
                        },
                        'then': {
                            '$divide': [
                                {'$ifNull': ['$match_count', 0]},
                                {'$size': {'$split': ['$combined_text', ' ']}}
                            ]
                        },
                        'else': 0
                    }
                }
            }
        },
        {
            '$sort': {'similarity': -1}
        },
        {
            '$limit': num
        }
        ]

        news_data = list(db_all[collection_name].aggregate(pipeline))

        # 将结果添加到 selected_news 列表中
        selected_news.extend(news_data)


    # 将全部主题的新闻按照相似度排序
    selected_news.sort(key=lambda x: x['similarity'], reverse=True)
    # 仅保留前4个结果
    selected_news = selected_news[:4]

    return selected_news
