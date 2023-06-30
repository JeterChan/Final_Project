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

def save_to_db(topic,data):
    # 新爬出的內容放進資料庫
    uri = "mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
    client = MongoClient(uri)
    # 选择要插入数据的数据库和集合
    db = client["TodayNews"]
    collection = db[topic]
# Send a ping to confirm a successful connection
    try:
        
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
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
            "views":0
            }
         # 插入数据
            collection.insert_one(insert_data)
    except Exception as e:
        print(e) 

def copy_to_db():
    # 連接到 MongoDB
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    source_db = client["TodayNews"]
    target_db = client["News"]

    # 获取集合名称列表
    collection_names = source_db.list_collection_names()
    # 打印集合名称
    for collection_name in collection_names:
        print(collection_name)
    
    for collection_name in collection_names:
        # 获取源集合中的所有文档
        source_collection = source_db[collection_name]
        documents = source_collection.find()

        # 将文档插入到目标集合
        target_collection = target_db[collection_name]
        target_collection.insert_many(documents)

def clean_todaydb():
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client["TodayNews"]
    # 获取集合名称列表
    collection_names = db.list_collection_names()
    for collection_name in collection_names:
        collection = db[collection_name]
        # 清除集合中的所有文档
        collection.delete_many({})
