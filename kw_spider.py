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

def grab_yahoo_usersearch(subtopic):
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=r"C:\Users\User\python-workspace\專題\chromedriver.exe",chrome_options=options)


    driver.get('https://tw.news.yahoo.com/')
    time.sleep(5)

    #找到關鍵字的element 並且將關鍵字輸入
    elem = driver.find_element(By.NAME, "p")
    elem.clear()
    ActionChains(driver).double_click(elem).perform()
    elem.send_keys(subtopic)
    elem.send_keys(Keys.RETURN)
    time.sleep(5)

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
    s_num = 0
    e_num = 1
    i = 0
    count = 0
    print('載入資料開始...')
    while count<1:
        i = i+1
        elements = driver.find_elements(By.CSS_SELECTOR, '#stream-container-scroll-template > li> div > div > div > div > h3')
        s_num = len(elements)

        elements[s_num - 1].location_once_scrolled_into_view  # 捲動加载資料
        time.sleep(5)  # 延遲1秒

        elements = driver.find_elements(By.CSS_SELECTOR, '#stream-container-scroll-template > li> div > div > div > div > h3')
        e_num = len(elements)
        print('捲動頁面到底部第 %d 次, 前次筆數= %d, 現在筆數= %d' % (i, s_num, e_num))
        count = count+1
    print("載入資料結束...")

    soup = BeautifulSoup(driver.page_source, 'lxml')
    print(soup)
    titles = soup.select('#stream-container-scroll-template > li> div > div > div > div > h3')
    driver.close()
    title_list = []
    count = 1
    for i,title in enumerate(titles):
        if (count%4)!=2: # 篩掉廣告
            print(count)
            print(title.text)
            title_list.append(title.text)

        count+=1

    return title_list
    

def check_duplicate(topic,subtopic,title_list): # 過濾掉資料庫內已經有的
    # 連接到 MongoDB
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client["News"]

    if topic in ["生活"] :
        collection = db["Life"]
    elif topic in ["運動"] :
        collection = db["Sport"]

    filtered_title = []
    
# 遍歷手上的資料清單
    for title in title_list:
        # 在資料庫中查找與當前標題相符的資料
        result = collection.find_one({'subtopic': subtopic,'title': title})
        
        # 如果找不到相符的資料，則將當前標題添加到篩選後的資料清單
        if result is None:
            filtered_title.append(title)

    # 印出篩選後的資料清單
    print("原本 :",title_list)
    print("篩選後 :",filtered_title)
    # 關閉與 MongoDB 的連接
    client.close()
    return filtered_title


def grab_yahoo_title_URL(title):
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=r"C:\Users\User\python-workspace\專題\chromedriver.exe",chrome_options=options)

    driver.get('https://tw.news.yahoo.com/')
    time.sleep(5)

    #讀取已經存在的記事本檔案，並將標題依序餵入後，點擊新聞取得網址，返回上一頁，
    URLs = []
    image_url = "none"

    try:
        elem = driver.find_element(By.NAME, "p")
        elem.clear()
        ActionChains(driver).double_click(elem).perform()
        elem.send_keys(title)
        elem.send_keys(Keys.RETURN)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'lxml')

        # 選取第一個標題旁的照片元素
        image = soup.select_one('.Cf')

        elem_title = driver.find_element(By.CLASS_NAME, "StreamMegaItem")
        ActionChains(driver).click(elem_title).perform()
        current_url = driver.current_url
        URLs.append(current_url)

        if image and image.find('img'):
            image_url = image.find('img')['src']

    except Exception:
        URLs.append("404")
    
    driver.quit()
    return URLs, image_url

def clean(subtopic, sentence_ws, sentence_pos):
    short_with_pos = []
    short_sentence = []
    if subtopic in ['美職']:
        stop_pos = set(['Neu','Neqa','Nh','Nep','Nd']) # 詞性不保留
        stop_word = set(['MLB','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    elif subtopic in ['中職']:
        stop_pos = set(['Nep', 'Nh', 'Neqa','Ncd','Nd','Neu']) #詞性不保留
        stop_word = set(['中職','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    elif subtopic in ['日職']:
        stop_pos = set(['Neqa','Nf','Neu','Ng','Ncd','Nh','Nep','Nd']) # 詞性不保留
        stop_word = set(['日職','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    elif subtopic in ['韓職']:
        stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd']) # 詞性不保留
        stop_word = set(['影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    elif subtopic in ['中信兄弟','味全龍','統一獅','樂天桃猿','富邦悍將','台鋼雄鷹']:
        stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd']) # 詞性不保留
        stop_word = set(['中職','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    elif subtopic in ['MLB 洋基','MLB 紅襪','MLB 光芒','MLB 金鶯','MLB 藍鳥','MLB 守護者','MLB 白襪','MLB 皇家','MLB 老虎','MLB 雙城','MLB 太空人','MLB 運動家','MLB 水手','MLB 天使','MLB 遊騎兵','MLB 大都會','MLB 勇士','MLB 費城人','MLB 馬林魚','MLB 國民','MLB 釀酒人','MLB 紅雀','MLB 紅人','MLB 小熊','MLB 海盜','MLB 響尾蛇','MLB 道奇','MLB 落磯','MLB 巨人','MLB 教士']:
        stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd','Ncd']) # 
        stop_word = set(['MLB','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
            is_N_or_V = pos.startswith("N") #or pos.startswith("V") 
            # 去掉名詞裡的某些詞性
            is_not_stop_pos = pos not in stop_pos
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 只剩一個字的詞也不留
            is_not_one_charactor = len(ws) != 1
            # 組成串列
            if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}") 
    elif subtopic in ['NBA']:
        stop_pos = set(['Neu','Neqa','Nh','Nep','Nd']) # 詞性不保留
        stop_word = set(['NBA','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['T1']:
        stop_pos = set(['Neu','Neqa','Nh','Nep','Nd']) # 詞性不保留
        stop_word = set(['T1','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['PLG']:
        stop_pos = set(['Neu','Neqa','Nh','Nep','Nd']) # 詞性不保留
        stop_word = set(['PLG','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['金州勇士',"波士頓塞爾蒂克","布魯克林籃網","紐約尼克","費城76人","多倫多暴龍","芝加哥公牛","克里夫蘭騎士",
                      "底特律活塞","印第安那溜馬","密爾瓦基公鹿","亞特蘭大老鷹","夏洛特黃蜂","邁阿密熱火","奧蘭多魔術","華盛頓巫師",
                      "洛杉磯快艇","洛杉磯湖人","鳳凰城太陽","沙加緬度國王","丹佛金塊","明尼蘇達灰狼","奧克拉荷馬雷霆","波特蘭拓荒者",
                      "猶他爵士","達拉斯獨行俠","休士頓火箭","曼斐斯灰熊","紐奧良鵜鶘","聖安東尼奧馬刺",]:
        stop_pos = set(['Nh','Nep','VH','VK','VC']) # 詞性不保留
        stop_word = set(['NBA','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['新北國王','臺北富邦勇士','桃園璞園領航猿','福爾摩沙台新夢想家','高雄17直播鋼鐵人','新竹街口攻城獅']:
        stop_pos = set(['Nh','Nep','VH','VK','VC']) # 詞性不保留
        stop_word = set(['PLG','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['新北中信特攻','臺南台鋼獵鷹','高雄全家海神','台灣啤酒英熊','臺中太陽','桃園永豐雲豹']:
        stop_pos = set(['Nh','Nep','VH','VHC','VC']) # 詞性不保留
        stop_word = set(['T1','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['足球']:
        stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd','Ncd']) # 
        stop_word = set(['足球','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") #or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['排球']:
        stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd','Ncd']) # 
        stop_word = set(['排球','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") #or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['田徑']:
        stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd','Ncd']) # 
        stop_word = set(['田徑','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") #or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")
    elif subtopic in ['氣象']:
        stop_pos = set(['Neu','Nf']) # 
        stop_word = set(['準氣象','氣象','快訊','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
                # 只留名詞
                is_N_or_V = pos.startswith("N") #or pos.startswith("V")
                # 去掉名詞裡的某些詞性
                is_not_stop_pos = pos not in stop_pos
                # 去掉"中職"這個詞
                is_not_stop_word = ws not in stop_word
                # 只剩一個字的詞也不留
                is_not_one_charactor = len(ws) != 1
                # 組成串列
                if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
                    short_with_pos.append(f"{ws}({pos})")
                    short_sentence.append(f"{ws}")                  
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

    if topic in ["生活"] :
        collection = db["Life"]
    elif topic in ["運動"] :
        collection = db["Sport"]

    #collection = db["TEST"]
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

def main(topic,subtopic):
    filtered_title_list=check_duplicate(topic,subtopic,grab_yahoo_usersearch(subtopic))
    for title in filtered_title_list:
        URL,image_url=grab_yahoo_title_URL(title)
        keywords=get_keyword(subtopic, title)
        copy_to_db(topic,dataframe(topic,subtopic,title,URL,image_url,keywords))

if __name__ == '__main__':
    topics=["運動","生活"]
                
    subtopics = ['足球','排球','田徑','中職','美職','日職','韓職','中信兄弟','味全龍','統一獅','樂天桃猿','富邦悍將','台鋼雄鷹',
                 'MLB 洋基','MLB 紅襪','MLB 光芒','MLB 金鶯','MLB 藍鳥','MLB 守護者','MLB 白襪','MLB 皇家','MLB 老虎','MLB 雙城','MLB 太空人','MLB 運動家','MLB 水手','MLB 天使',
                 'MLB 遊騎兵','MLB 大都會','MLB 勇士','MLB 費城人','MLB 馬林魚','MLB 國民','MLB 釀酒人','MLB 紅雀','MLB 紅人','MLB 小熊','MLB 海盜','MLB 響尾蛇','MLB 道奇','MLB 落磯','MLB 巨人','MLB 教士',
                 "NBA","波士頓塞爾蒂克","布魯克林籃網","紐約尼克","費城76人","多倫多暴龍","芝加哥公牛","克里夫蘭騎士","底特律活塞","印第安那溜馬","密爾瓦基公鹿","亞特蘭大老鷹",
                 "夏洛特黃蜂","邁阿密熱火","奧蘭多魔術","華盛頓巫師","金州勇士","洛杉磯快艇","洛杉磯湖人","鳳凰城太陽","沙加緬度國王","丹佛金塊","明尼蘇達灰狼","奧克拉荷馬雷霆",
                 "波特蘭拓荒者","猶他爵士","達拉斯獨行俠","休士頓火箭","曼斐斯灰熊","紐奧良鵜鶘","聖安東尼奧馬刺",
                 "PLG",'新北國王','臺北富邦勇士','桃園璞園領航猿','福爾摩沙台新夢想家','高雄17直播鋼鐵人','新竹街口攻城獅',
                 "T1",'新北中信特攻','臺南台鋼獵鷹','高雄全家海神','台灣啤酒英熊','臺中太陽','桃園永豐雲豹']
    for topic in topics:
        if topic in ["運動"]:
            for subtopic in subtopics:
                print(f"Processing topic: {topic},subtopic: {subtopic}")
                main(topic,subtopic)
        else :
            print(f"Processing topic: {topic},subtopic: 氣象")
            main(topic,"氣象")
