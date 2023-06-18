from flask import Flask,render_template,url_for,redirect,request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import jsonify
 
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
login_manager.login_view = 'log_in'

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

# 建立網站首頁的回應方式
@app.route("/")
def index(): # 用來回應網站首頁連線的函式
    return render_template('index.html') # 回應網站首頁的內容

@app.route("/index")
def homepage():
    return redirect(url_for('index'))

@app.route("/hot_package")
def hot_package():
    # topic, subtopic, img_url 資料庫抓資料
    return render_template('hot_package.html',
                           topic="",
                           subtopic="",
                           img_url="")

@app.route("/choose_function",methods=["GET","POST"])
def choose_function():
    if request.method == "GET":
        email = request.args.get("email","")
        password = request.args.get("pwd","")
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["pwd"]
    print("Email:" + email + "\nPassword:" + password)
    # 測試輸入有沒有抓到輸入的帳號密碼
    return render_template('choose_function.html')


@app.route("/register",methods=['GET','POST'])
def register():
    if request.method == 'POST':
        input_email = request.form['email']
        input_name=request.form['username']
        input_password = request.form['password']
        input_repeat_password = request.form['password-repeat']

        # email、password為空，驗證失敗轉回登入頁面
        if not input_email or not input_password or not input_name:
            flash('Invalid input.')
            return redirect(url_for('register'))
        if input_password != input_repeat_password:
            flash('Two passwords are different.')
            return redirect(url_for('register'))
        if User.query.filter_by(email=input_email).first():
            flash('Email has already been registered.')
            return redirect(url_for('register'))
        if User.query.filter_by(username=input_name).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        
        user = User(email=input_email,username=input_name, password=input_password)
        
        # add to db table
        # 將使用者物件加入資料庫會話
        #db.session.add(user)
        # 提交資料庫變更
        #db.session.commit()

        flash("Thank you for registering.")
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/show/<topic>/<subtopic>')
@login_required
def show(topic, subtopic):
    db = myclient["News"]
    collection = db[topic]
    data = collection.find({'subtopic': subtopic})
    news_list = []

    for document in reversed(data):
        news = {
            'title': document['title'],
            'news_url': document['url'],
            'img_url': document['image'],
        }
        news_list.append(news)

    return render_template('show.html', 
                           package_title='組合包名稱',
                           topic=topic,
                           subtopic=subtopic,
                           keyword='',
                           news_list=news_list)


# google sign in
GOOGLE_OAUTH2_CLIENT_ID = '774374692298-jtj2he5qpci5mdblvaucvgolgastlo8t.apps.googleusercontent.com'

# 登入功能
@app.route("/log_in",methods=['GET','POST'])
def log_in():
    if request.method == 'POST':
        input_email = request.form['email']
        input_password = request.form['password']

        # email、password為空，驗證失敗轉回登入頁面
        if not input_email or not input_password:
            flash('Invalid input.')
            return redirect(url_for('log_in'))
        
        #  要去抓資料庫的資料
        user = User.query.filter_by(email=input_email).first()

        if user.check_password(input_password) and user is not None:
            login_user(user)  # 登入用戶
            flash('Login success.')
        # 驗證成功跳轉主頁
            return redirect(url_for('home'))  # 重定向到主頁
        
        flash('Invalid email or password.')  # 如果驗證失敗，顯示錯誤消息
        return redirect(url_for('log_in'))  # 重定向回登錄頁面
    
    return render_template('log_in.html', google_oauth2_client_id=GOOGLE_OAUTH2_CLIENT_ID)

@app.route('/google_sign_in', methods=['POST'])
def google_sign_in():
    token = request.json['id_token']
    
    try:
        # Specify the GOOGLE_OAUTH2_CLIENT_ID of the app that accesses the backend:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_OAUTH2_CLIENT_ID
        )

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # user_id = id_info['sub']
        # reference: https://developers.google.com/identity/sign-in/web/backend-auth
    except ValueError:
        # Invalid token
        raise ValueError('Invalid token')
 
    print('登入成功')
    return jsonify({}), 200


# 登出功能
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout success.")
    return redirect(url_for('/'))


# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)
