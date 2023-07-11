#資料庫
from pymongo import MongoClient

def check_duplicate(topic,subtopic,title_list,URL_list,image_list): # 過濾掉資料庫內已經有的
    # 連接到 MongoDB
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client["News"]
    collection = db[topic]

    filtered_title = []
    filtered_url=[]
    filtered_image=[]

# 遍歷手上的資料清單
    for title,url,image in zip(title_list,URL_list,image_list):
        # 在資料庫中查找與當前標題相符的資料
        result = collection.find_one({'subtopic': subtopic,'title': title})
        
        # 如果找不到相符的資料，則將當前標題添加到篩選後的資料清單
        if result is None:
            filtered_title.append(title)
            filtered_url.append(url)
            filtered_image.append(image)
    # 關閉與 MongoDB 的連接
    client.close()
    return filtered_title,filtered_url,filtered_image

def save_to_db(db_name,topic,data):
    # 連接到 MongoDB
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client[db_name]
    collection = db[topic]
# Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    
        if db_name == "關鍵每一天":
            # 获取要插入的数据
            for index,row in data.iterrows():
                # 取得標題和網址的值
                all_keywords = row['ALL_Keyword']
                date=row['Date'] 
                insert_data = {
                'keywords': all_keywords,
                'date': date
                }
        else:
            # 获取要插入的数据
            for index,row in data.iterrows():
                # 取得標題和網址的值
                topic = row['Topic']  
                subtopic = row['Subtopic']  
                title = row['Title']  
                url = row['URL'] 
                image = row['Image'] 
                keyword = row['Keyword']
                content=row['Content']
                summary=row['Summary'] 
                emotion_value=row['Emotion_value'] 
                new_keyword=row['New_keyword']
                date=row['Date']
                insert_data = {
                "topic":topic,
                "subtopic":subtopic,
                "title": title,
                "url":url,
                "image":image,
                "keyword":keyword,
                "content":content,
                "summary":summary,
                "emotion_value":emotion_value,
                "views":0,
                "new_keyword":new_keyword,
                "date":date
                }
         # 插入数据
            collection.insert_one(insert_data)
    except Exception as e:
        print(e) 
    # 關閉與 MongoDB 的連接
    client.close()

def copy_to_db():
    # 連接到 MongoDB
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    source_db = client["TodayNews"]
    target_db = client["News"]

    # 获取集合名称列表
    collection_names = source_db.list_collection_names()
    
    for collection_name in collection_names:
        # 获取源集合中的所有文档
        source_collection = source_db[collection_name]
        documents = source_collection.find()

        # 将文档插入到目标集合
        target_collection = target_db[collection_name]
        for document in documents:
            # 刪除 _id
            del document['_id']
            # 插入文檔到目標集合
            target_collection.insert_one(document)
    # 關閉與 MongoDB 的連接
    client.close()
    print("DB複製完成!")

def clean_todaydb():
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client["TodayNews"]
    # 获取集合名称列表
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        collection = db[collection_name]
        # 清除集合中的所有文档
        collection.delete_many({})
    # 關閉與 MongoDB 的連接
    client.close()

def get_all_data(clientnm,item):
    item_list=[]
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client[clientnm]
    # 获取集合名称列表
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        # 获取源集合中的所有文档
        collection = db[collection_name]
        for document in collection.find():
            item_list.append(document[item])
    # 關閉與 MongoDB 的連接
    client.close()
    return item_list

def get_col_data(collection_name):
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db_today= client["TodayNews"]
    kw_list=[]
    collection = db_today[collection_name]
    for document in collection.find():
        kw_list.append(document['new_keyword'])
        date =document['date']
    return  kw_list,date
