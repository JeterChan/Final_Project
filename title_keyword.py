#模擬按鍵行為用套件
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
import requests
import json

#爬蟲用
from bs4 import BeautifulSoup 
import time

# 斷詞用
from ckip_transformers import __version__
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker

# KeyBert
from keybert import KeyBERT

# 資料處理
import pandas as pd


#下面這一串資料是在把通知關掉
options = webdriver.ChromeOptions()  
prefs = {'profile.default_content_setting_values':{'notifications': 2}}
options.add_experimental_option('prefs', prefs)
options.add_argument("disable-infobars")
driver = webdriver.Chrome(executable_path=r"D:\Project\selenium\chromedriver.exe",chrome_options=options)

def grab_yahoo_usersearch(topic):
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=r"D:\Project\selenium\chromedriver.exe",chrome_options=options)

    driver.get('https://tw.news.yahoo.com/')
    time.sleep(5)

    #找到關鍵字的element 並且將關鍵字輸入
    elem = driver.find_element(By.NAME, "p")
    elem.clear()
    ActionChains(driver).double_click(elem).perform()
    elem.send_keys(topic)
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
        time.sleep(3)  # 延遲3秒

        elements = driver.find_elements(By.CSS_SELECTOR, '#stream-container-scroll-template > li> div > div > div > div > h3')
        e_num = len(elements)
        print('捲動頁面到底部第 %d 次, 前次筆數= %d, 現在筆數= %d' % (i, s_num, e_num))
        count = count+1
    print("載入資料結束...")

    soup = BeautifulSoup(driver.page_source, 'lxml')
    
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
    
    
    title_df = pd.DataFrame(title_list,columns=['Title']) # 將 title_list 轉成 dataframe
    title_df.to_csv("D:/Project/selenium/nba/nba_title.csv",index=False,encoding='utf-8')
    break_word(title_list)

    # file.close()



def clean(sentence_ws, sentence_pos):
  short_with_pos = []
  short_sentence = []
  stop_pos = set(['Nep', 'Nh']) # 這 2 種詞性不保留 - 代名詞、指定代名詞
  stop_word = set([topic]) # 停用詞-topic
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

def break_word(text):

    # Initialize drivers
    print("Initializing drivers ... WS")
    ws_driver = CkipWordSegmenter(model="bert-base", device=-1)
    print("Initializing drivers ... POS")
    pos_driver = CkipPosTagger(model="bert-base", device=-1)
    print("Initializing drivers ... NER")
    print()

    ws = ws_driver(text)
    pos = pos_driver(ws)

    ws_file = open("D:/Project/selenium/nba/nba_ws.txt","r+",encoding='utf-8') # 'r+' 代表可讀可寫
    pos_file = open("D:/Project/selenium/nba/nba_pos.txt","w",encoding='utf-8')

    print()
    print('=====')

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        print("原文：")
        print(sentence)
        (short, res) = clean(sentence_ws, sentence_pos)
        print("斷詞後：")
        print(short)
        ws_file.write(short+"\n")
        print()
        print("斷詞後+詞性標注：")
        print(res)
        pos_file.write(res+"\n")
        print('=====')
    

    get_keyword(ws_file)

def remove_blank(ws_file):
    with open("D:/Project/selenium/nba/nba_ws.txt","w",encoding="utf-8") as ws_noblank:

        for line in ws_file:
            if line.strip():
                ws_noblank.write(line)
        ws_noblank.close()

def get_keyword(ws_file):
    kw_file = open("D:/Project/selenium/nba/nba_kw.txt","w",encoding="utf-8")
    
    kw_model = KeyBERT()
    for doc in ws_file:
        keywords = kw_model.extract_keywords(doc,keyphrase_ngram_range=(1,1),use_mmr=True, diversity=0.2,top_n=3)
        for keyword in keywords: #跑三次，因top_n=3
            kw_file.write(keyword[0]+" ")
        kw_file.write("\n")
        print(keywords)
    

    kw_file.close()

if __name__ == '__main__':
    topic = 'NBA'
    grab_yahoo_usersearch(topic)
    