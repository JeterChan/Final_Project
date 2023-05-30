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
    

def check_duplicate(title_list): # 過濾掉資料庫內已經有的
    # 連接到 MongoDB
    client = MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
    db = client["News"]
    collection = db["Sport"]

    filtered_title = []

# 遍歷手上的資料清單
    for title in title_list:
        # 在資料庫中查找與當前標題相符的資料
        result = collection.find_one({'Title': title})
        
        # 如果找不到相符的資料，則將當前標題添加到篩選後的資料清單
        if result is None:
            filtered_title.append(title)

    # 印出篩選後的資料清單
    print(filtered_title)
    # 關閉與 MongoDB 的連接
    client.close()
    return filtered_title


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
        #print("目前標題："+title)
        #print("Current URL:", current_url)
    
    return(URLs)

def clean(sentence_ws, sentence_pos):
  short_with_pos = []
  short_sentence = []
  stop_pos = set([]) # 詞性不保留 
  stop_word = set([""]) # 停用詞-topic
  for word_ws, word_pos in zip(sentence_ws, sentence_pos):
    # 只留名詞和動詞
    is_N_or_V = word_pos.startswith("V") or word_pos.startswith("N")
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
  return (" ".join(short_sentence), " ".join(short_with_pos))

# ckip 斷詞
def break_word(text):
    ws = ws_driver(text)
    pos = pos_driver(ws)

    ws_list = [] # 用來儲存斷詞結果的list

    print()
    print('=====')

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        print("原文：")
        print(sentence)
        (short, res) = clean(sentence_ws, sentence_pos) # 清理不需要的字詞
        print("斷詞後：")
        print(short)
        ws_list.append(short)
        print()
        print("斷詞後+詞性標注：")
        print(res)
        print('=====')
    print(ws_list)

    return ws_list # 回傳斷詞後的list, 不會有空行的問題  

# 抓關鍵字
def get_keyword(filtered_title_list):
    ws_list=break_word(filtered_title_list)

    kw_model = KeyBERT()

    for doc in ws_list:
        keywords = kw_model.extract_keywords(doc,keyphrase_ngram_range=(1,1),use_mmr=True, diversity=0.2,top_n=3)
        print(keywords)
    # 提取關鍵字列表
    keyword_list = []
    for keyword, _ in keywords:
        keyword_list.append(keyword) 

    return keyword_list

def dataframe(filtered_title_list,URLs,keywords):
    data = pd.DataFrame({'Title': filtered_title_list, 'URL': URLs,'Keyword':keywords}) # 創建dataframe    
    return data

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

        for row in data.iterrows():
            # 取得標題和網址的值
            title = row['Title']
            url = row['URL']
            keyword = row['Keyword']
            data = {
            "subtopic":subtopic,
            "title": title,
            "url":url,
            "keyword":keyword
            }
         # 插入数据
            collection.insert_one(data)
    except Exception as e:
        print(e) 

def main(subtopic):
    filtered_title_list=check_duplicate(grab_yahoo_usersearch(subtopic))
    URLs=grab_yahoo_title_URL(filtered_title_list)
    keywords=get_keyword(filtered_title_list)
    copy_to_db(dataframe(filtered_title_list,URLs,keywords))

if __name__ == '__main__':
    subtopics = ['棒球','中職','美職','日職','韓職','中信兄弟','味全龍','統一獅','樂天桃猿','富邦悍將','台鋼雄鷹','MLB 洋基','MLB 紅襪','MLB 光芒','MLB 金鶯','MLB 藍鳥','MLB 守護者','MLB 白襪','MLB 皇家','MLB 老虎','MLB 雙城','MLB 太空人','MLB 運動家','MLB 水手','MLB 天使','MLB 遊騎兵','MLB 大都會','MLB 勇士','MLB 費城人','MLB 馬林魚','MLB 國民','MLB 釀酒人','MLB 紅雀','MLB 紅人','MLB 小熊','MLB 海盜','MLB 響尾蛇','MLB 道奇','MLB 落磯','MLB 巨人','MLB 教士']
    for subtopic in subtopics:
        main(subtopic)
