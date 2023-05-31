from pymongo import MongoClient
import pandas as pd
from ckip_transformers import __version__
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
# KeyBert
from keybert import KeyBERT
import time
from ckip_transformers import __version__
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
#模擬按鍵行為用套件
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 

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

def copy_to_db(data):
    # 新爬出的內容放進資料庫
    uri = "mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
    client = MongoClient(uri)
    # 选择要插入数据的数据库和集合
    db = client["News"]
    collection = db["Sport"]
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
            keyword = row['Keyword']  
            insert_data = {
            "topic":topic,
            "subtopic":subtopic,
            "title": title,
            "url":url,
            "keyword":keyword
            }
         # 插入数据
            collection.insert_one(insert_data)
    except Exception as e:
        print(e) 


def clean(subtopic, sentence_ws, sentence_pos):
    short_with_pos = []
    short_sentence = []
    if subtopic in ['美職']:
        stop_pos = set(['Neu','Neqa','Nh','Nep','Nd']) # 詞性不保留
        stop_word = set(['MLB','影','圖']) # 停用詞
        for ws, pos in zip(sentence_ws, sentence_pos):
            # 只留名詞和動詞
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
def get_keyword(subtopic,title):
    ws_list=break_word(subtopic,title)

    kw_model = KeyBERT()
    keywords = []
    for doc in ws_list:
        keywords_score = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,1), use_mmr=True, diversity=0.2, top_n=3)
        doc_keywords = [keyword for keyword, score in keywords_score]
        keywords.append(" ".join(doc_keywords))

    return keywords


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
    
    
    #print("目前標題："+title)
    try:
        elem = driver.find_element(By.NAME, "p")
        elem.clear()
        ActionChains(driver).double_click(elem).perform()
        elem.send_keys(title)
        elem.send_keys(Keys.RETURN)
        time.sleep(5)

        elem_title = driver.find_element(By.CLASS_NAME, "StreamMegaItem")
        ActionChains(driver).click(elem_title).perform()
        current_url = driver.current_url
        URLs.append(current_url)
        print("Current URL:", current_url)
    except Exception:
        URLs.append("404")  # 找不到網址時添加空白字串
    driver.quit()
    return(URLs)

def get_data():
    # 读取Excel文件
    df = pd.read_excel('資料庫.xlsx')
    
    for _, row in df.iterrows():
        # 提取每列的数据
        topic = row['主題']
        subtopic = row['次主題']
        title = row['標題']
        URL=grab_yahoo_title_URL(title)
        keywords=get_keyword(subtopic,title)  
        # 打印结果
        print("Topic:", topic)
        print("Subtopic:", subtopic)
        print("Title:", title)
        print("URL:", URL)
        print("Keyword:", keywords)
        # 创建新的DataFrame
        data = pd.DataFrame({'Topic': topic, 'Subtopic': subtopic,'Title': title, 'URL': URL,'Keyword':keywords})#
        # 打印结果
        print(data)
        copy_to_db(data)

if __name__ == '__main__':
    get_data()
