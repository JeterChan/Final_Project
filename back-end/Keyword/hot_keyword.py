from collections import Counter

def calculate_keywords(kw_list):
    
    keyword_counts = Counter()
    all_keywords=[]
    for kw in zip(kw_list):
        #print(kw)
        keyword=kw[0].split(" ")
        keyword_counts.update(keyword)
        
    top_keywords = keyword_counts.most_common(10)
    #print("出現頻率最高")
    for keyword, count in top_keywords:
        #print(keyword, ":", count)
        all_keywords.append(keyword)

    return all_keywords
    
