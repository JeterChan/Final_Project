
from concurrent.futures import ThreadPoolExecutor
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
import search_news
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
    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.email  
    
@login_manager.user_loader  
def user_loader(user_id):  
    db = connect_db()
    cursor = db.cursor()
    query = "SELECT * FROM tb_user WHERE email = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        email = result['email']
        password = result['password']
        user = User(email, password)
        return user
    return None


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

def get_collection_data(topic):
    db = myclient['News']
    collection = db[topic]

    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$limit": 50}
    ]

    data = collection.aggregate(pipeline)
    return list(data)


# 建立網站首頁的回應方式
@app.route("/")
def index():
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]

    combined_data = []
    # 使用线程池并行处理获取数据
    with ThreadPoolExecutor() as executor:
        # 并行获取各个主题的数据
        futures = [executor.submit(get_collection_data, topic) for topic in topics]

        # 收集各个主题的数据
        for future in futures:
            combined_data.extend(future.result())

    # 按照timestamp字段排序
    sorted_data = sorted(combined_data, key=lambda x: x['timestamp'], reverse=True)

    return render_template('newest.html', news_list=sorted_data)


@app.route("/newest")
def newest():
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]

    combined_data = []
    # 使用线程池并行处理获取数据
    with ThreadPoolExecutor() as executor:
        # 并行获取各个主题的数据
        futures = [executor.submit(get_collection_data, topic) for topic in topics]

        # 收集各个主题的数据
        for future in futures:
            combined_data.extend(future.result())

    # 按照timestamp字段排序
    sorted_data = sorted(combined_data, key=lambda x: x['timestamp'], reverse=True)

    return render_template('newest.html', news_list=sorted_data)

@app.route("/hot")
def hot():
    search_news("綜合全部")
    return render_template('hot.html')

@app.route("/recommendation")
@login_required
def recommendation():
    return render_template('recommendation.html')


@app.route("/collection")
@login_required
def collection():
    return render_template('collection.html')

@app.route("/login",methods=['GET','POST'])
def login():
    db = connect_db()
    if request.method == 'POST':
        # 获取表单数据
        input_email = request.form['email']
        input_password = request.form['password']

        # 查询数据库以获取用户
        cursor = db.cursor()
        query = "SELECT * FROM tb_user WHERE email = %s"
        cursor.execute(query, (input_email,))
        result = cursor.fetchone()

        # 验证邮箱和密码
        if result and check_password_hash(result['password'], input_password):
            # 构造 User 对象
            user = User(result['email'], result['password'])
            login_user(user)  # 登录用户
            flash('Login success.')
            return redirect(url_for('afterlogin'))  # 重定向到主页

        flash('Invalid email or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页

    return render_template('login.html')


@app.route("/register",methods=['GET','POST'])
def register():
    db = connect_db()
    if request.method == 'POST':
        # 获取表单数据
        input_email = request.form['email']
        input_password = request.form['password']
        input_repeat_password = request.form['password-repeat']

        # 验证输入
        if input_password != input_repeat_password:
            flash('Two passwords are different.')
            return redirect(url_for('register'))

        # 检查是否已注册
        cursor = db.cursor()
        query = "SELECT * FROM tb_user WHERE email = %s"
        cursor.execute(query, (input_email,))
        result = cursor.fetchone()
        if result:
            flash('Email has already been registered.')
            return redirect(url_for('register'))

        # 生成密码哈希值
        password_hash = generate_password_hash(input_password)

        # 执行插入操作
        query = "INSERT INTO tb_user (email, password) VALUES (%s, %s)"
        cursor.execute(query, (input_email, password_hash))
        db.commit()

        flash("Thank you for registering.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/index_login")
@login_required
def afterlogin():
    db = myclient["News"]
    topics=["運動","生活","國際","娛樂","社會地方","科技","健康","財經"]
    news_data = []
    for topic in topics:
        collection = db[topic]
        collection.create_index([("date", -1)])

        pipeline = [
            {"$match": {"date": "20230709", "topic": topic}},
            {"$sample": {"size": 2}}
        ]

        topic_news = list(collection.aggregate(pipeline))
        news_data.append({"topic": topic, "news_list": topic_news})

    return render_template('index_login.html', news_data=news_data)

@app.route("/login_hot")
@login_required
def login_hot():
    return render_template('login_hot.html')

@app.route("/logout")
@login_required
def logout():
    # 登出用户
    logout_user()

    # 移除会话的持久性
    session.permanent = False

    # 移除会话数据
    session.clear()

    # 重定向到登录页或其他页面
    return redirect(url_for('login'))



# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)
