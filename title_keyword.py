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

    file = open(r"D:\Project\selenium\nba\nba.txt","w",encoding='utf-8')
    title_list = []
    count = 1
    for i,title in enumerate(titles):
        if (count%4)!=2: # 篩掉廣告
            print(count)
            print(title.text)
            title_list.append(title.text)
            file.write(title.text.strip()+"\n") # 爬蟲完存成txt檔

        count+=1

    data = pd.DataFrame(title_list,columns=['Title'])
    ws_list = break_word(title_list) #呼叫斷詞function
    get_keyword(ws_list,data) # 呼叫抓關鍵字的函式
    
    

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

# ckip 斷詞
def break_word(text):

    # Initialize drivers
    print("Initializing drivers ... WS")
    ws_driver = CkipWordSegmenter(model="bert-base", device=-1)
    print("Initializing drivers ... POS")
    pos_driver = CkipPosTagger(model="bert-base", device=-1)
    print()

    ws = ws_driver(text)
    pos = pos_driver(ws)

    ws_file = open(r"D:/Project/selenium/nba/nba_ws.txt","w",encoding='utf-8')
    pos_file = open(r"D:/Project/selenium/nba/nba_pos.txt","w",encoding='utf-8')

    ws_list = []

    print()
    print('=====')

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        print("原文：")
        print(sentence)
        (short, res) = clean(sentence_ws, sentence_pos)
        print("斷詞後：")
        print(short)
        ws_list.append(short)
        ws_file.write(short+"\n")
        print()
        print("斷詞後+詞性標注：")
        print(res)
        pos_file.write(res+"\n")
        print('=====')
    print(ws_list)

    return ws_list # 回傳斷詞後的list, 不會有空行的問題  

# 抓關鍵字
def get_keyword(ws_list,data):
    kw_file = open("D:/Project/selenium/nba/nba_kw.txt","w",encoding="utf-8")
    data = data.reindex(columns=['Title','Keyword_1','Keyword_2','Keyword_3'],fill_value='0') # 新增 Keyword 欄位,預測值為 '0'

    kw_model = KeyBERT()
    row = 0 # 從第 0 列開始
    column = 1 # 從第 1 行開始 
    for doc in ws_list:
        keywords = kw_model.extract_keywords(doc,keyphrase_ngram_range=(1,1),use_mmr=True, diversity=0.2,top_n=3)
        for keyword in keywords: #跑三次，因top_n=3, 抓出來的關鍵字個數多少就會跑幾次，至多三次
            kw_file.write(keyword[0]+" ") # keyword[0]是string
            data.loc[row,'Keyword_'+str(column)] = keyword[0] # 將關鍵字一筆一筆加入keyword欄位,從keyword_1~keyword_3
            column += 1 # 移動欄位 Keyword_1 => Keyword_2 => Keyword_3

        kw_file.write("\n")
        column = 1 # 新增完一個標題的關鍵字後,將欄位移回Keyword_1    
        row += 1 # 往下一標題繼續新增關鍵字
    
        print(keywords)
    
    data.to_csv('D:/Project/selenium/nba/nba.csv',index=False,encoding='utf-8') # 把 data 存成 csv 檔
    kw_file.close()

if __name__ == '__main__':
    topic = 'NBA'
    grab_yahoo_usersearch(topic)
    