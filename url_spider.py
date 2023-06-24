from pymongo import MongoClient
#模擬按鍵行為用套件
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys 
# 資料處理
import pandas as pd
#爬蟲用
from bs4 import BeautifulSoup 
import time
from ckip_transformers import __version__
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
# KeyBert
from keybert import KeyBERT
#摘要
import requests
import jieba
import numpy as np
import collections
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer  
import re


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

def dataframe(topic,subtopic,title,URL,image_url,keywords,content,summary):
    data = pd.DataFrame({'Topic': topic, 'Subtopic': subtopic,'Title': title, 'URL': URL,'Image':image_url,'Keyword':keywords,'Content':content,'Summary':summary}) # 創建dataframe    
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
            content=row['Contnet']
            summary=row['Summary']  
            insert_data = {
            "topic":topic,
            "subtopic":subtopic,
            "title": title,
            "url":url,
            "image":image,
            "keyword":keyword,
            "content":content,
            "summary":summary
            }
         # 插入数据
            collection.insert_one(insert_data)
    except Exception as e:
        print(e) 

def split_sentence(text, punctuation_list=r'!?。！？"'):  #按標點分割句子
    sentence_set = []
    inx_position = 0
    char_position = 0
    for char in text:
        char_position += 1
        if char in punctuation_list:
            next_char = list(text[inx_position:char_position+1]).pop()
            if next_char not in punctuation_list:
                sentence_set.append(text[inx_position:char_position])
                inx_position = char_position
    if inx_position < len(text):
        sentence_set.append(text[inx_position:])
    sentence_with_index = {i:sent for i,sent in enumerate(sentence_set)}
    return sentence_set,sentence_with_index

def get_tfidf_matrix(sentence_set,stop_word):  #移除停用詞並轉換為矩陣
    corpus = []
    for sent in sentence_set:
        sent_cut = jieba.cut(sent, cut_all=False)
        sent_list = [word for word in sent_cut if word not in stop_word]
        sent_str = ' '.join(sent_list)
        corpus.append(sent_str)
    vectorizer=CountVectorizer()
    transformer=TfidfTransformer()
    tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))
    tfidf_matrix=tfidf.toarray()
    return np.array(tfidf_matrix)

def get_sentence_with_words_weight(tfidf_matrix):  #計算句子權重
    sentence_with_words_weight = {}
    for i in range(len(tfidf_matrix)):
        sentence_with_words_weight[i] = np.sum(tfidf_matrix[i])
    max_weight = max(sentence_with_words_weight.values()) #归一化
    min_weight = min(sentence_with_words_weight.values())
    for key in sentence_with_words_weight.keys():
        x = sentence_with_words_weight[key]
        sentence_with_words_weight[key] = (x-min_weight)/(max_weight-min_weight)
    return sentence_with_words_weight

def get_sentence_with_position_weight(sentence_set):  #計算位置權重
    sentence_with_position_weight = {}
    total_sent = len(sentence_set)
    for i in range(total_sent):
        sentence_with_position_weight[i] = (total_sent - i) / total_sent
    return sentence_with_position_weight

def similarity(sent1,sent2):  #計算兩句子相似度
    return np.sum(sent1 * sent2) / 1e-6+(np.sqrt(np.sum(sent1 * sent1)) * np.sqrt(np.sum(sent2 * sent2)))

def get_similarity_weight(tfidf_matrix):  #計算相似度權重
    sentence_score = collections.defaultdict(lambda :0.)
    for i in range(len(tfidf_matrix)):
        score_i = 0.
        for j in range(len(tfidf_matrix)):
            score_i += similarity(tfidf_matrix[i],tfidf_matrix[j])
        sentence_score[i] = score_i
    max_score = max(sentence_score.values()) #归一化
    min_score = min(sentence_score.values())
    for key in sentence_score.keys():
        x = sentence_score[key]
        sentence_score[key] = (x-min_score)/(max_score-min_score)
    return sentence_score

def ranking_base_on_weigth(sentence_with_words_weight,  #按句子權重排序
                            sentence_with_position_weight,
                            sentence_score, feature_weight):
    sentence_weight = collections.defaultdict(lambda :0.)
    for sent in sentence_score.keys():
        sentence_weight[sent] = feature_weight[0]*sentence_with_words_weight[sent] +\
                                feature_weight[1]*sentence_with_position_weight[sent] +\
                                feature_weight[2]*sentence_score[sent]
    sort_sent_weight = sorted(sentence_weight.items(),key=lambda d: d[1], reverse=True)
    return sort_sent_weight

def get_summarization(sentence_with_index,sort_sent_weight,topK_ratio):  #取得摘要
    topK = int(len(sort_sent_weight)*topK_ratio)
    summarization_sent = sorted([sent[0] for sent in sort_sent_weight[:topK]])
    summarization = []
    for i in summarization_sent:
        summarization.append(sentence_with_index[i])
    summary = ''.join(summarization)

     # 檢查摘要是否為空白，如果是則提高 topK_ratio 值並重新生成摘要
    if summary.strip() == '':
        topK_ratio += 0.05
        return get_summarization(sentence_with_index ,sort_sent_weight, topK_ratio)
    chars_to_remove = r" -」)_!?。！？'）】.%"  # 要刪除的字元
    processed_summary = summary.lstrip(chars_to_remove)
    return processed_summary  

def get_content(url):

    response = requests.get(url)
     # 检查响应的状态码
    if response.status_code == 404:
        text_content="404"
    else:
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        caas_body = soup.find('div', class_='caas-body')  # 選取class為'caas-body'的<div>元素
        paragraphs = caas_body.find_all('p')  # 在選取的<div>元素中尋找所有<p>標籤

        # 使用正則表達式去除贅字    #【記者 王苡蘋╱高雄 報導】                        #【記者陳雅芳／彰化報導】                        #（記者王乙徹／台中報導）                        #鄉民中心／李育道報導                          #記者陳金龍∕南投報導                        #娛樂中心/洪雨汝 報導
        pattern_A = re.compile(r'(\【+[^\s]*\s*[^\s]*\s*\╱+\s*[^\s]*\s*報導\】)|([^\s]*\s*[^\s]+\s*\／+\s*[^\s]*\s*報導\】)|([^\s]*\s*[^\s]*\s*\／+\s*[^\s]*\s*報導\）)|([^\s]*\s*[^\s]*\s*\／+\s*[^\s]*\s*報導)|([^\s]*\s*[^\s]*\s*\∕+\s*[^\s]*\s*報導)|([^\s]*\s*[^\s]*\s*\/+\s*[^\s]*\s*報導)')
                                #[NOWnews今日新聞]           #（中央社記者劉冠廷台北23日電）     #（路透巴黎23日電）              #（觀傳媒新北新聞）                 #[Newtalk新聞]              #【健康醫療網／編輯部整理】
        pattern_B= re.compile(r'(\[+\s*NOWnews今日新聞+\s*\])|(\（+\s*中央社+\s*[^\s]*\s*\）)|(\（+\s*路透+\s*[^\s]*\s*\）)|(\（+\s*觀傳媒+\s*[^\s]*\s*\）)|(\[+\s*Newtalk新聞+\s*\])|(\【健康醫療網\／編輯部整理\】)')
                                # 匹配「更多」後面的任意字元（包括換行符號）直到行尾 
                                            #更多民視新聞報導 #更多 NOWnews 今日新聞 報導 #更多 TVBS 報導                                  #看更多 CTWANT 文章
        pattern_C = re.compile(r'(延伸閱讀.*$)|(查看原文.*$)|(原始連結.*$)|(更多+\s*[^\s]*\s*[^\s]*報導.*$)|(更多+\s*[^\s]*\s*[^\s]*新聞.*$)|(看更多+\s*[^\s]*\s*[^\s]*文章.*$)')  
        text_content = ' '.join([(pattern_C.sub('',pattern_B.sub('', pattern_A.sub('', p.get_text())))) for p in paragraphs])

    return text_content

# 停用詞
stops = []
with open('專題\stopWord_summar.txt', 'r', encoding='utf-8-sig') as f:
    for line in f.readlines():
        stops.append(line.strip())

def main(topic,subtopic,spider_url):
    title_list,URL_list,image_list=grab_yahoo_usersearch(spider_url)
    filtered_title_list,filtered_URL_list,filtered_image_list=check_duplicate(topic,subtopic,title_list,URL_list,image_list)
    for title,URL,image_url in zip(filtered_title_list,filtered_URL_list,filtered_image_list):
        content=get_content(URL)                            #取得該網址的新聞內容
        sentences, indexs =split_sentence(content)          # 按標點分割句子
        tfidf = get_tfidf_matrix(sentences, stops)             # 移除停用詞並轉換為矩陣
        word_weight =get_sentence_with_words_weight(tfidf)    # 計算句子關鍵詞權重
        posi_weight = get_sentence_with_position_weight(sentences)     # 計算位置權重
        scores = get_similarity_weight(tfidf)                  # 計算相似度權重
        sort_weight = ranking_base_on_weigth(word_weight, posi_weight, scores, feature_weight=[3,0,2]) #按句子權重排序
        summary = get_summarization(indexs ,sort_weight, topK_ratio=0.2) # 取得摘要比例
        keywords=get_keyword(subtopic, title)                   #取標題的關鍵字
        copy_to_db(topic,dataframe(topic,subtopic,title,URL,image_url,keywords,content,summary))  #放進資料庫

if __name__ == '__main__':
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"] #
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
