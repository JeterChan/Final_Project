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

#停用詞
stops = []
with open('Keyword\stopwordsnew.txt', 'r', encoding='utf-8-sig') as f:
    for line in f.readlines():
        stops.append(line.strip())

def clean(sentence_ws, sentence_pos):
    short_with_pos = []
    short_sentence = []
    stop_pos = set([]) # 詞性不保留
    stop_word = set(['影','圖']) # 停用詞
    for ws, pos in zip(sentence_ws, sentence_pos):
            # 去掉"中職"這個詞
            is_not_stop_word = ws not in stop_word
            # 組成串列
            if  is_not_stop_word : 
                short_with_pos.append(f"{ws}({pos})")
                short_sentence.append(f"{ws}")
    return (" ".join(short_sentence), " ".join(short_with_pos))

# ckip 斷詞
def break_word(text):
    ws = ws_driver([text])
    pos = pos_driver(ws)

    ws_list = [] # 用來儲存斷詞結果的list

    for sentence, sentence_ws, sentence_pos in zip(text, ws, pos):
        (short, res) = clean( sentence_ws, sentence_pos)  # 清理不需要的字詞
        ws_list.append(short)


    return ws_list # 回傳斷詞後的list, 不會有空行的問題 

# 抓關鍵字
def kw_get_keyword(summary):
    ws_list=break_word(summary)

    kw_model = KeyBERT()
    keywords = []
    for doc in ws_list:
        keywords_score = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,1), use_mmr=True, diversity=0.2, top_n=1)
        doc_keywords = [keyword for keyword, score in keywords_score]
        keywords.append(" ".join(doc_keywords))
    print(keywords)
    return keywords

sentences=["若想改善便秘情形，可以看大便的狀態，決定要補充蔬菜還是水果，像是如果沒有便意，又連續好多天沒有大便時，可以多攝取容易帶動便意的「非水溶性膳食纖維」也就是深綠色蔬菜；若有便意，但糞便又黏又硬石，就要多攝取「水溶性膳食纖維」，也就是水果，來讓大便變軟。 鍾雲霓也提醒，如果是因為便秘要補充纖維質，喝蔬果汁或將蔬菜燉爛都行；雖然過度烹調可能會破壞蔬菜的營養成分，但是對纖維卻不會產生太大的影響，就連吃炸杏鮑菇或花椰菜泥都可以有效補充纖維質。" ]
for sentence in sentences:
    kw_get_keyword(sentence)
