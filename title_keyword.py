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

# 抓當天日期
from datetime import date

def grab_yahoo_usersearch(subtopic):
    #下面這一串資料是在把通知關掉
    options = webdriver.ChromeOptions()  
    prefs = {'profile.default_content_setting_values':{'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("disable-infobars")
    driver = webdriver.Chrome(executable_path=r"D:\Project\selenium\chromedriver.exe",chrome_options=options)
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
    elem.send_keys(subtopic)
    elem.send_keys(Keys.RETURN)
    time.sleep(5)

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)") 
    s_num = 0
    e_num = 1
    i = 0
    count = 0
    print('載入資料開始...')
    while count<3: # 設定爬蟲次數
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

    ### 看爬蟲出來的結果
    # file = open(topic+".txt","w",encoding='utf-8')
    title_list = []
    count = 1
    for i,title in enumerate(titles):
        if (count%4)!=2: # 篩掉廣告
            print(count)
            print(title.text)
            title_list.append(title.text)
            # file.write(title.text.strip()+"\n") # 爬蟲完存成txt檔

        count+=1

    data = pd.DataFrame(title_list,columns=['Title']) # 創建dataframe
    ws_list = break_word(subtopic,title_list) #呼叫斷詞function
    data = get_keyword(ws_list,data) # 呼叫抓關鍵字的函式
    return data
    

def clean(subtopic,sentence_ws, sentence_pos):
    short_with_pos = []
    short_sentence = []
    if subtopic in ['NBA']:
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
    return (" ".join(short_sentence), " ".join(short_with_pos))

# ckip 斷詞
def break_word(subtopic,text):

    # Initialize drivers
    print("Initializing drivers ... WS")
    ws_driver = CkipWordSegmenter(model="bert-base", device=-1)
    print("Initializing drivers ... POS")
    pos_driver = CkipPosTagger(model="bert-base", device=-1)
    print()

    ws = ws_driver(text)
    pos = pos_driver(ws)

    ### 可以拿來看斷詞後的結果如何
    # ws_file = open("ws.txt","w",encoding='utf-8')
    pos_file = open("pos.txt","w",encoding='utf-8')

    ws_list = [] # 用來儲存斷詞結果的list

    print()
    print('=====')

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        print("原文：")
        print(sentence)
        (short, res) = clean(subtopic,sentence_ws, sentence_pos) # 清理不需要的字詞
        print("斷詞後：")
        print(short)
        ws_list.append(short)
        # ws_file.write(short+"\n")
        print()
        print("斷詞後+詞性標注：")
        print(res)
        pos_file.write(res+"\n")
        print('=====')
    print(ws_list)

    return ws_list # 回傳斷詞後的list, 不會有空行的問題  

# 抓關鍵字
def get_keyword(ws_list,data):
    # kw_file = open("kw.txt","w",encoding="utf-8")
    data = data.reindex(columns=['Title','Keyword_1','Keyword_2','Keyword_3'],fill_value='0') # 新增 Keyword 欄位,預測值為 '0'

    kw_model = KeyBERT()
    row = 0 # 從第 0 列開始
    column = 1 # 從第 1 行開始 
    for doc in ws_list:
        keywords = kw_model.extract_keywords(doc,keyphrase_ngram_range=(1,1),use_mmr=True, diversity=0.2,top_n=3)
        for keyword in keywords: #跑三次，因top_n=3, 抓出來的關鍵字個數多少就會跑幾次，至多三次
            # kw_file.write(keyword[0]+" ") # keyword[0]是string
            data.loc[row,'Keyword_'+str(column)] = keyword[0] # 將關鍵字一筆一筆加入keyword欄位,從keyword_1~keyword_3
            column += 1 # 移動欄位 Keyword_1 => Keyword_2 => Keyword_3

        # kw_file.write("\n")
        column = 1 # 新增完一個標題的關鍵字後,將欄位移回Keyword_1    
        row += 1 # 往下一標題繼續新增關鍵字
    
        print(keywords)
    return data
    
    # kw_file.close()

if __name__ == '__main__':
    subtopics = ["NBA","波士頓塞爾蒂克","布魯克林籃網","紐約尼克","費城76人","多倫多暴龍","芝加哥公牛","克里夫蘭騎士","底特律活塞","印第安那溜馬","密爾瓦基公鹿","亞特蘭大老鷹",
                 "夏洛特黃蜂","邁阿密熱火","奧蘭多魔術","華盛頓巫師","金州勇士","洛杉磯快艇","洛杉磯湖人","鳳凰城太陽","沙加緬度國王","丹佛金塊","明尼蘇達灰狼","奧克拉荷馬雷霆",
                 "波特蘭拓荒者","猶他爵士","達拉斯獨行俠","休士頓火箭","曼斐斯灰熊","紐奧良鵜鶘","聖安東尼奧馬刺",
                "PLG",'新北國王','臺北富邦勇士','桃園璞園領航猿','福爾摩沙台新夢想家','高雄17直播鋼鐵人','新竹街口攻城獅',
                "T1",'新北中信特攻','臺南台鋼獵鷹','高雄全家海神','台灣啤酒英熊','臺中太陽','桃園永豐雲豹'
                ]
    for subtopic in subtopics:
        data = grab_yahoo_usersearch(subtopic)
        today = date.today()
        data.to_csv(str(today)+'-'+subtopic+'.csv',index=False,encoding='utf-8') # 把 data 存成 csv 檔