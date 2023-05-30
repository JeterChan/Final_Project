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


def clean(subtopic,sentence_ws, sentence_pos):
  short_with_pos = []
  short_sentence = []
  if subtopic in ['中職']:
    stop_pos = set(['Nep', 'Nh', 'Neqa','Ncd','Nd','Neu']) #詞性不保留
    stop_word = set(['中職','影','圖']) # 停用詞
    for word_ws, word_pos in zip(sentence_ws, sentence_pos):
        # 只留名詞和動詞
        is_N_or_V = word_pos.startswith("N") #or word_pos.startswith("V") 
        # 去掉名詞裡的某些詞性
        is_not_stop_pos = word_pos not in stop_pos
        # 去掉"中職"這個詞
        is_not_stop_word = word_ws not in stop_word
        # 只剩一個字的詞也不留
        is_not_one_charactor = not (len(word_ws) == 1)
        # 組成串列
        if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
            short_with_pos.append(f"{word_ws}({word_pos})")
            short_sentence.append(f"{word_ws}")
  elif subtopic in ['棒球']:
    stop_pos = set(['Neu', 'Nh', 'Neqa','Nep','Nd']) # 詞性不保留
    stop_word = set(['影','圖']) # 停用詞
    for word_ws, word_pos in zip(sentence_ws, sentence_pos):
        # 只留名詞和動詞
        is_N_or_V = word_pos.startswith("N") #or word_pos.startswith("V") 
        # 去掉名詞裡的某些詞性
        is_not_stop_pos = word_pos not in stop_pos
        # 去掉停用詞
        is_not_stop_word = word_ws not in stop_word
        # 只剩一個字的詞也不留
        is_not_one_charactor = not (len(word_ws) == 1)
        # 組成串列
        if is_N_or_V and is_not_stop_pos and is_not_stop_word and is_not_one_charactor:
            short_with_pos.append(f"{word_ws}({word_pos})")
            short_sentence.append(f"{word_ws}")
  elif subtopic in ['美職']:
    stop_pos = set(['Neu','Neqa','Nh','Nep','Nd']) # 詞性不保留
    stop_word = set(['MLB','影','圖']) # 停用詞
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
  elif subtopic in ['日職']:
    stop_pos = set(['Neqa','Nf','Neu','Ng','Ncd','Nh','Nep','Nd']) # 詞性不保留
    stop_word = set(['日職','影','圖']) # 停用詞
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
  elif subtopic in ['韓職']:
    stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd']) # 詞性不保留
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
  elif subtopic in ['中信兄弟','味全龍','統一獅','樂天桃猿','富邦悍將','台鋼雄鷹']:
    stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd']) # 詞性不保留
    stop_word = set(['中職','影','圖']) # 停用詞
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
  elif subtopic in ['MLB 洋基','MLB 紅襪','MLB 光芒','MLB 金鶯','MLB 藍鳥','MLB 守護者','MLB 白襪','MLB 皇家','MLB 老虎','MLB 雙城','MLB 太空人','MLB 運動家','MLB 水手','MLB 天使','MLB 遊騎兵','MLB 大都會','MLB 勇士','MLB 費城人','MLB 馬林魚','MLB 國民','MLB 釀酒人','MLB 紅雀','MLB 紅人','MLB 小熊','MLB 海盜','MLB 響尾蛇','MLB 道奇','MLB 落磯','MLB 巨人','MLB 教士']:
    stop_pos = set(['Neu','Nf','Nh','Ng','Nes','Nep','Neqa','Nd','Ncd']) # 
    stop_word = set(['MLB','影','圖']) # 停用詞
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
  return (" ".join(short_sentence), " ".join(short_with_pos))

# ckip 斷詞
def break_word(subtopic,text):
    ws = ws_driver(text)
    pos = pos_driver(ws)

    ws_list = [] # 用來儲存斷詞結果的list

    #print()
    #print('=====')

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        #print("原文：")
        #print(sentence)
        (short, res) = clean(subtopic,sentence_ws, sentence_pos) # 清理不需要的字詞
        #print("斷詞後：")
        #print(short)
        ws_list.append(short)
        #print()
        #print("斷詞後+詞性標注：")
        #print(res)
        #print('=====')
    #print(ws_list)

    return ws_list # 回傳斷詞後的list, 不會有空行的問題  

# 抓關鍵字
def get_keyword(subtopic,filtered_title_list):
    ws_list=break_word(subtopic,filtered_title_list)

    kw_model = KeyBERT()
    keywords = []
    for doc in ws_list:
        keywords_score = kw_model.extract_keywords(doc,keyphrase_ngram_range=(1,1),use_mmr=True, diversity=0.2,top_n=3)
        doc_keywords = [keyword for keyword, score in keywords_score]
        keywords.append(" ".join(doc_keywords))

    return keywords

def grab_yahoo_title_URL(filtered_title_list):
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=r"C:\Users\User\python-workspace\專題\chromedriver.exe",chrome_options=options)

    driver.get('https://tw.news.yahoo.com/')
    time.sleep(5)

    #讀取已經存在的記事本檔案，並將標題依序餵入後，點擊新聞取得網址，返回上一頁，
    URLs = []
    
    for title in filtered_title_list:
        print("目前標題："+title)
        #找到關鍵字的element 並且將關鍵字輸入
        elem = driver.find_element(By.NAME, "p")
        elem.clear()
        ActionChains(driver).double_click(elem).perform()
        elem.send_keys(title)
        elem.send_keys(Keys.RETURN)
        time.sleep(5)

        elem_title = driver.find_element(By.CLASS_NAME,"StreamMegaItem")
        ActionChains(driver).click(elem_title).perform()

        current_url = driver.current_url
        URLs.append(current_url) 
        print("Current URL:", current_url)
    
    return(URLs)

def get_data():
    # 读取Excel文件
    df = pd.read_excel('資料庫.xlsx')

    # 提取每列的数据
    topic = df['主題']
    subtopic = df['次主題']
    title = df['標題']
    URLs=grab_yahoo_title_URL(title)
    keywords=get_keyword(subtopic,title)  
    
    # 创建新的DataFrame
    data = pd.DataFrame({'Topic': topic, 'Subtopic': subtopic,'Title': title, 'URL': URLs,'Keyword':keywords})#

    # 打印结果
    print(data)
    return data

if __name__ == '__main__':
    data=get_data()
    copy_to_db(data)  