from pymongo import MongoClient
#模擬按鍵行為用套件
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
#from pymongo import MongoClient,ServerApi
# 資料處理
import pandas as pd
#爬蟲用
from bs4 import BeautifulSoup 
import time
from ckip_transformers import __version__
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
# KeyBert
from keybert import KeyBERT

# Initialize drivers
print("Initializing drivers ... WS")
ws_driver = CkipWordSegmenter(model="bert-base", device=-1)
print("Initializing drivers ... POS")
pos_driver = CkipPosTagger(model="bert-base", device=-1)
print("Initializing drivers ... NER")
ner_driver = CkipNerChunker(model="bert-base", device=-1)
print("Initializing drivers ... all done")
print()

#下面這一串資料是在把通知關掉
options = webdriver.ChromeOptions() 
prefs = {'profile.default_content_setting_values':{'notifications': 2}}
options.add_experimental_option('prefs', prefs)
options.add_argument("disable-infobars")
driver = webdriver.Chrome(executable_path=r"C:\Users\User\python-workspace\專題\chromedriver.exe",chrome_options=options)

def grab_yahoo_usersearch(spider_url):
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=r"C:\Users\User\python-workspace\專題\chromedriver.exe",chrome_options=options)


    driver.get(spider_url)
    time.sleep(5)

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
    s_num = 0
    e_num = 1
    i = 0
    count = 0
    print('載入資料開始...')
    while count<10:
        i = i+1
        elements = driver.find_elements(By.CSS_SELECTOR,  'h3')
        s_num = len(elements)

        elements[s_num - 1].location_once_scrolled_into_view  # 捲動加载資料
        time.sleep(5)  # 延遲1秒

        elements = driver.find_elements(By.CSS_SELECTOR,  'h3')
        e_num = len(elements)
        print('捲動頁面到底部第 %d 次, 前次筆數= %d, 現在筆數= %d' % (i, s_num, e_num))
        count = count+1
    print("載入資料結束...")

    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    titles = soup.select( 'h3')
    URLs_elem = soup.select('h3 > a')
    images = soup.select('.Cf')

    driver.close()
    title_list = []
    URL_list = []
    image_list = []

    count = 1
    for title,URL,image in zip(titles,URLs_elem,images):
        if (count%4)!=2: # 篩掉廣告
            title_list.append(title.text)

            URL = 'https://tw.news.yahoo.com/'+URL['href']
            URL_list.append(URL)

            if image and image.find('img'):
                image_list.append(image.find('img')['src'])
            else:
                image_list.append("None")

        count+=1

    return title_list,URL_list,image_list
    

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

    # 印出篩選後的資料清單
    #print("原本 :",title_list)
    #print("篩選後 :",filtered_title)
    #print("原本 :",URL_list)
    #print("篩選後 :",filtered_url)
    #print("原本 :",image_list)
    #print("篩選後 :",filtered_image)
    # 關閉與 MongoDB 的連接
    client.close()
    return filtered_title,filtered_url,filtered_image




def clean(subtopic, sentence_ws, sentence_pos):
    short_with_pos = []
    short_sentence = []
    if subtopic in ['棒球']:
        stop_pos = set(['Neu', 'Nh', 'Neqa','Nep','Nd']) # 詞性不保留
        stop_word = set(['影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    elif subtopic in ['籃球','網球','高爾夫球']:
        stop_pos = set(["Nd",'Neu','Nes','Nh']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['美食消費']:
        stop_pos = set(["Nd",'Neu','Nes','Nh','V_2','Nf','Ncd']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['旅遊交通']:  
        stop_pos = set(['Neu','Nep','Nh']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['文教']: 
        stop_pos = set([]) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['兩性親子']: 
        stop_pos = set(['Neu','Nd','Neqa']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") #or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['新奇']:
        stop_pos = set(['Ng']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos  and is_not_stop_word: #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}") 
    elif subtopic in ['亞澳', '中港澳', '歐非', '美洲']: 
        stop_pos = set(['Ncd','Neu','Neqa']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") #or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['日韓娛樂']:
        stop_pos = set(['Neqa','Neu','VJ','Nf']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word: #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}") 
    elif subtopic in ['藝人動態']:
        stop_pos = set(['Neu','VF','Nh','Ng']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word: #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['音樂']: 
        stop_pos = set(['Neu','Neqa','Ng']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word : #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}")
    elif subtopic in ['電影戲劇','大台北', '北台灣','中部離島', '南台灣', '東台灣','科技新知', '遊戲相關', '3C家電', '手機iOS', '手機Android','養生飲食', '癌症', '塑身減重', '慢性病']: 
        stop_pos = set(['Neu','Neqa']) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word: #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}") 
    elif subtopic in ["股市匯市","房地產","產業動態","理財就業"]:
        stop_pos = set([]) # 
        stop_word = set(['影','圖']) # 停用詞
        for word_ws, word_pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = word_pos.startswith("N") or word_pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = word_pos not in stop_pos
            # 去掉停用詞
            is_not_stop_word = word_ws not in stop_word
            # 只剩一個字的詞也不留
            #is_not_one_charactor = not (len(word_ws) == 1)
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word: #and is_not_one_charactor
                short_with_pos.append(f"{word_ws}({word_pos})")
                short_sentence.append(f"{word_ws}") 
    return (" ".join(short_sentence), " ".join(short_with_pos))

# ckip 斷詞
def break_word(subtopic,text):
    ws = ws_driver([text])
    pos = pos_driver(ws)

    ws_list = [] # 用來儲存斷詞結果的list

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        (short, res) = clean(subtopic, sentence_ws, sentence_pos)  # 清理不需要的字詞
        ws_list.append(short)


    return ws_list # 回傳斷詞後的list, 不會有空行的問題 

# 抓關鍵字
def get_keyword(subtopic, title):
    ws_list=break_word(subtopic,title)

    kw_model = KeyBERT()
    keywords = []
    for doc in ws_list:
        keywords_score = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,1), use_mmr=True, diversity=0.2, top_n=3)
        doc_keywords = [keyword for keyword, score in keywords_score]
        keywords.append(" ".join(doc_keywords))

    return keywords

def dataframe(topic,subtopic,title,URL,image_url,keywords):
    data = pd.DataFrame({'Topic': topic, 'Subtopic': subtopic,'Title': title, 'URL': URL,'Image':image_url,'Keyword':keywords}) # 創建dataframe    
    return data

def copy_to_db(topic,data):
    # 新爬出的內容放進資料庫
    uri = "mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
    client = MongoClient(uri)
    # 选择要插入数据的数据库和集合
    db = client["News"]
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
            insert_data = {
            "topic":topic,
            "subtopic":subtopic,
            "title": title,
            "url":url,
            "image":image,
            "keyword":keyword
            }
         # 插入数据
            collection.insert_one(insert_data)
    except Exception as e:
        print(e) 

def main(topic,subtopic,spider_url):
    title_list,URL_list,image_list=grab_yahoo_usersearch(spider_url)
    filtered_title_list,filtered_URL_list,filtered_image_list=check_duplicate(topic,subtopic,title_list,URL_list,image_list)
    for title,URL,image_url in zip(filtered_title_list,filtered_URL_list,filtered_image_list):
        keywords=get_keyword(subtopic, title)
        copy_to_db(topic,dataframe(topic,subtopic,title,URL,image_url,keywords))

if __name__ == '__main__':
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康"] #
    for topic in topics:
        if topic in ["運動"]:
            subtopics = ["棒球", "籃球", "網球", "高爾夫球"]
            spider_urls=["https://tw.news.yahoo.com/baseball/",
                        "https://tw.news.yahoo.com/basketball/",
                        "https://tw.news.yahoo.com/tennis/",
                        "https://tw.news.yahoo.com/tennis/"]
        elif topic in ["生活"]:
             subtopics = ["美食消費", "旅遊交通", "文教", "兩性親子","新奇"]
             spider_urls=["https://tw.news.yahoo.com/consumption/",
                         "https://tw.news.yahoo.com/travel/",
                         "https://tw.news.yahoo.com/art-edu/",
                         "https://tw.news.yahoo.com/family-gender/",
                         "https://tw.news.yahoo.com/odd/"]
                        
        elif topic in ["國際"]:
             subtopics = ["亞澳", "中港澳", "歐非", "美洲"]
             spider_urls=["https://tw.news.yahoo.com/asia-australia/",
                         "https://tw.news.yahoo.com/china/",
                         "https://tw.news.yahoo.com/euro-africa/",
                         "https://tw.news.yahoo.com/america/"]
        elif topic in ["娛樂"]:
             subtopics = ["日韓娛樂", "藝人動態", "音樂", "電影戲劇"] 
             spider_urls=["https://tw.news.yahoo.com/jp-kr/",
                         "https://tw.news.yahoo.com/celebrity/",
                         "https://tw.news.yahoo.com/music/",
                         "https://tw.news.yahoo.com/tv-radio/"] 
        elif topic in ["社會地方"]:
             subtopics = ["大台北", "北台灣", "中部離島", "南台灣", "東台灣"]
             spider_urls=["https://tw.news.yahoo.com/taipei/",
                         "https://tw.news.yahoo.com/north-taiwan/",
                         "https://tw.news.yahoo.com/mid-taiwan/",
                         "https://tw.news.yahoo.com/south-taiwan/",
                         "https://tw.news.yahoo.com/east-taiwan/"]
        elif topic in ["科技"]:
             subtopics = ["科技新知", "遊戲相關", "3C家電", "手機iOS", "手機Android"]
             spider_urls=["https://tw.news.yahoo.com/tech-development/",
                         "https://tw.news.yahoo.com/game/",
                         "https://tw.news.yahoo.com/3c-appliances/",
                         "https://tw.news.yahoo.com/applephone/",
                         "https://tw.news.yahoo.com/androidphone/"]
        elif topic in ["健康"]:
             subtopics = ["養生飲食", "癌症", "塑身減重", "慢性病"]
             spider_urls=["https://tw.news.yahoo.com/fitness/",
                          "https://tw.news.yahoo.com/cancer/",
                          "https://tw.news.yahoo.com/beauty/",
                          "https://tw.news.yahoo.com/disease/"
                         ]
        elif topic in ["財經"]:
             subtopics = ["股市匯市","房地產","產業動態","理財就業"]
             spider_urls=["https://tw.news.yahoo.com/stock/",
                          "https://tw.news.yahoo.com/real-estate/",
                          "https://tw.news.yahoo.com/industry/",
                          "https://tw.news.yahoo.com/money-career/"
                         ]
        for subtopic, spider_url in zip(subtopics, spider_urls):
            print(f"Processing topic: {topic},subtopic: {subtopic}")
            main(topic, subtopic, spider_url)
