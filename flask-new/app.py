import random
from flask import Flask,render_template,url_for,redirect,request, flash,session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import jsonify
import pymysql
from authlib.integrations.flask_client import OAuth

myclient = pymongo.MongoClient("mongodb+srv://user1:user1@cluster0.ronm576.mongodb.net/?retryWrites=true&w=majority")

app = Flask( 
    __name__,
    static_folder='static',
    static_url_path='/'
)
#  會使用到session，故為必設
app.secret_key = 'NCUMIS' 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):

    #TODO:要連db

    def __init__(self, email, username, password):
        #初始化
        self.email = email
        self.username = username
        # 實際存入的為password_hash，而非password本身
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        #檢查使用者密碼
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader  
def user_loader(user_id):  
    user = User.query.get(int(user_id)) 
    return user  # 返回用戶對象

def connect_db():
    # 資料庫設定
    db_settings = {
        "host": "finalproject.cluster-cnfzqwsf4fd2.ap-southeast-2.rds.amazonaws.com",
        "port": 3306,
        "user": "ncumis",
        "password": "ncumis12345",
        "db": "Final_Project",
        "charset": "utf8"
    }
    try:
        # 建立Connection物件
        conn = pymysql.connect(**db_settings)
        return conn
    except Exception as ex:
        print(ex)

# 建立網站首頁的回應方式
@app.route("/")
def index(): # 用來回應網站首頁連線的函式
    return render_template('newest.html') # 回應網站首頁的內容

@app.route("/index")
def homepage():
    return redirect(url_for('newest'))

@app.route("/newest")
def newest():
    db = myclient["News"]
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]
    nums=[1000,300,600,500,700,103,200,500]
    news_data = []
    for topic,num in zip(topics,nums):
        collection=db[topic]
        data = list(collection.find().skip(collection.count_documents({}) - num))
        random_indexes = random.sample(range(len(data)), 2)
        random_data = [data[i] for i in random_indexes]
        news_data.append({"topic": topic, "news_list": random_data})

    return render_template('newest.html', news_data=news_data)

@app.route("/hot")
def hot():
    db = myclient["關鍵每一天"]
    collection=db["綜合全部"]
    return render_template('hot.html')

@app.route("/recommendation")
#@login_required
def recommendation():
    return render_template('recommendation.html')


@app.route("/collection")
#@login_required
def collection():
    return render_template('collection.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/index_login")
def afterlogin():
    return render_template('index_login.html')

# google sign in



# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)
