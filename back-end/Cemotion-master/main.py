#按文本字符串分析
from cemotion import Cemotion
from hanziconv import HanziConv #將彎彎字體改成簡體字
import pymongo

c = Cemotion()

myclient = pymongo.MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["News"]
topics=["運動"]#"運動","生活","國際","娛樂","社會地方","科技","健康","財經"
for topic in topics:
    mycol = mydb[topic]
    for document in mycol.find():
        if "emotion_value" not in document:
            summary = document['summary']
            processed_summary=HanziConv.toSimplified(summary)
            emotion_value=c.predict(processed_summary)
            emotion_value = float("{:.6f}".format(emotion_value))  # 将浮点数转换为小数部分只保留6位小数的float类型
            # 更新資料庫的每一筆記錄
            mycol.update_one({"_id": document["_id"]}, {"$set": {"emotion_value": emotion_value}})
            #在正式存資料庫之前先檢查一下有沒有對
            #print('"', summary , '"\n' , '预测值:{:6f}'.format(c.predict(processed_summary) ) , '\n')
            #print(emotion_value)
            print(document["_id"],"已完成")