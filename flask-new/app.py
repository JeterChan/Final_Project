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
    static_url_path='/newest'
)
#  會使用到session，故為必設
app.secret_key = 'NCUMIS' 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email, password):
        #初始化
        self.email = email
        # 實際存入的為password_hash，而非password本身
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        #檢查使用者密碼
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader  
def user_loader(user_id):  
    user = User.query.get(int(user_id)) 
    return user  # 返回用戶對象

# 建立資料庫連接
def connect_db():
    db_settings = {
        "host": "finalproject.cluster-cnfzqwsf4fd2.ap-southeast-2.rds.amazonaws.com",
        "port": 3306,
        "user": "ncumis",
        "password": "ncumis12345",
        "db": "Final_Project",
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor
    }
    connection = pymysql.connect(**db_settings)
    return connection


# 建立網站首頁的回應方式
@app.route("/")
def index():
    db = myclient["News"]
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]
    news_data = []
    for topic in topics:
        collection=db[topic]
        data = list(collection.find({"date":"20230709"}))
        random_indexes = random.sample(range(len(data)), 2)
        random_data = [data[i] for i in random_indexes]
        news_data.append({"topic": topic, "news_list": random_data})

    return render_template('newest.html', news_data=news_data)

@app.route("/index")
def homepage():
    return redirect(url_for('newest'))

@app.route("/newest")
def newest():
    db = myclient["News"]
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]
    news_data = []
    for topic in topics:
        collection=db[topic]
        data = list(collection.find({"date":"20230709"}))
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

@app.route("/login",methods=['GET','POST'])
def log_in():
    if request.method == 'POST':
        input_email = request.form['email']
        input_password = request.form['password']
        
        #  要去抓資料庫的資料
        user = User.query.filter_by(email=input_email).first()

        if user.check_password(input_password) and user is not None:
            login_user(user)  # 登入用戶
            flash('Login success.')
        # 驗證成功跳轉主頁
            return redirect(url_for('home'))  # 重定向到主頁
        
        flash('Invalid email or password.')  # 如果驗證失敗，顯示錯誤消息
        return redirect(url_for('login'))  # 重定向回登錄頁面
    
    return render_template('login.html')


@app.route("/register",methods=['GET','POST'])
def register():
    db = connect_db()
    if request.method == 'POST':
        # 獲取表單數據
        input_email = request.form['email']
        input_password = request.form['password']
        input_repeat_password = request.form['password-repeat']

        # 驗證輸入
        if input_password != input_repeat_password:
            flash('Two passwords are different.')
            return redirect(url_for('register'))
        
        # 檢查是否已註冊
        cursor = db.cursor()
        query = "SELECT * FROM tb_user WHERE email = %s"
        cursor.execute(query, (input_email,))
        result = cursor.fetchone()
        if result:
            flash('Email has already been registered.')
            return redirect(url_for('register'))
        
        # 執行插入操作
        query = "INSERT INTO tb_user (email, password) VALUES (%s, %s)"
        cursor.execute(query, (input_email, input_password))
        db.commit()

        flash("Thank you for registering.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/index_login")
def afterlogin():
    return render_template('index_login.html')

# google sign in



# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)
