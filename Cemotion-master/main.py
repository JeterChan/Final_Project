#按文本字符串分析
from cemotion import Cemotion
from hanziconv import HanziConv #將彎彎字體改成簡體字


str_text1 = HanziConv.toSimplified('隨著氣候變遷與經濟成長需求，全球已出現糧食短缺的危機！早在2008年，聯合國糧農組織就已推動「馬鈴薯年」運動，建議少吃米、麥，多攝取栽培方法簡單、單位產量高、且澱粉與蛋白質含量皆高於穀類的馬鈴薯，作為主食。從種植的角度來說，馬鈴薯即使在高山、寒冷、日照不佳的環境也能生長，且全球各地皆有高產量，加上經濟實惠的價格、多變的料理方式，讓它成為最受歡迎的國民美食。美國新鮮馬鈴薯多元的品種和豐富的營養成分，提供大眾新鮮的選擇和全新的機會，更是廚師們探索各種料理方式時不可或缺的完美夥伴。此外，經過冷凍或脫水的馬鈴薯，可大幅延長保存期限，且仍具有豐富的營養價值—富含維生素C、鉀、纖維、維生素B6等，對於有麩質過敏的民眾，更是安心、無麩質的好選擇。')
str_text2 = HanziConv.toSimplified('院線看電影這麼多年以來，這是我第一次看電影睡著了。簡直是史上最大爛片！沒有之一！侮辱智商！大家小心警惕！千萬不要上當！再也不要看了！')
str_text3 = HanziConv.toSimplified('「#MeToo」風暴從政壇延燒到演藝圈，藝人NONO（陳宣裕）被網紅直播主「小紅老師」指控性騷擾，受害者多達近20人，即使NONO已與朱海君結婚仍不斷侵犯女性，NONO隨後也發文宣布停止演藝工作。而朱海君先前曾上節目爆料NONO一簽結婚證書就變了一個人，揭開兩人結婚10年的婚姻內幕。')
str_text4 = HanziConv.toSimplified('美國海岸防衛隊23日宣布發現潛水器「泰坦號」殘骸，確認5名乘客全數罹難。當年拍攝紅遍全球電影《鐵達尼號》導演兼深海探險家的詹姆斯‧柯麥隆說，這具旅遊潛水器的許多安全警告均遭忽視，更認為鐵達尼號的前車之鑑與此次「泰坦號」悲劇十分相似，同樣都是警告沒人理睬、在同一地點發生，也是多國協力投入水下搜救，坦言「這實在令人震驚」。')
str_text5 = HanziConv.toSimplified('中華職棒樂天球團，在樂天桃園球場舉辦「辣年糕趴」，啦啦隊女神李多慧生涯首度站上台灣棒球場的投手丘受邀開球，韓國樂天(Lotte)女孩啦啦隊也特別到場應援，並且跟台灣超人氣的樂天女孩林襄同場互尬舞蹈，展現兩國不同的青春活力，讓許多球迷都嗨翻天。')
str_text6 = HanziConv.toSimplified('柯文哲更自爆民眾黨區域立委找不到人、沒有地方黨部，雖全台有14位民眾黨議員，但都是剛選上的，他也問過北市議員「學姊」黃瀞瑩，黃也沒有參選意願。廖筱君反問，既然如此，憑什麼敢選總統？柯文哲說，自己就是按部就班，可以選就選、不能選就算了，更突然爆出一句「我不需要參選證明，只需要退選證明，若不要選，退選要宣布」')
str_text7 = HanziConv.toSimplified('熱到狗狗也受不了！一名中國網友分享家中寵物趣事，他日前出門遛狗，沒想到遛到一半，狗狗卻突然不見，讓他感到非常驚慌，趕緊回家叫家人幫忙找。豈料，該名網友一回到家卻發現狗狗早已坐在家門口，似乎是熱到自己搭電梯跑回家。')
str_text8 = HanziConv.toSimplified('需留意西半部的午後雷陣雨甚至可能延續到晚上')

delimiter = "，"
c = Cemotion()


print('"', str_text1 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text1) ) , '\n')
print('"', str_text2 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text2) ) , '\n')
print('"', str_text3 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text3) ) , '\n')
print('"', str_text4 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text4) ) , '\n')
print('"', str_text5 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text5) ) , '\n')
print('"', str_text6 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text6) ) , '\n')
print('"', str_text7 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text7) ) , '\n')
print('"', str_text8 , '"\n' , '预测值:{:6f}'.format(c.predict(str_text8) ) , '\n')

#使用列表进行批量分析
from cemotion import Cemotion

list_text = ['内饰蛮年轻的，而且看上去质感都蛮好，貌似本田所有车都有点相似，满高档的！',
'总而言之，是一家不会再去的店。']

c = Cemotion()
print(c.predict(list_text))