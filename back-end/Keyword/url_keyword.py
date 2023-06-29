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
def url_get_keyword(subtopic, title):
    ws_list=break_word(subtopic,title)

    kw_model = KeyBERT()
    keywords = []
    for doc in ws_list:
        keywords_score = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,1), use_mmr=True, diversity=0.2, top_n=3)
        doc_keywords = [keyword for keyword, score in keywords_score]
        keywords.append(" ".join(doc_keywords))

    return keywords