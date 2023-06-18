from flask import Flask,render_template,url_for,redirect,request
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import jsonify

app = Flask(
    __name__,
    static_folder='static',
    static_url_path='/'
)

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

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/show")
def show():
    # package_title　topic subtopic keyword title news_url img_url 要去資料庫抓
    return render_template('show.html',
                           package_title='NBA',
                           topic='運動',
                           subtopic='NBA',
                           keyword='',
                           title='這是測試',
                           news_url='https://tw.news.yahoo.com/search?p=nba&fr=uh3_news_web&fr2=p%3Anews%2Cm%3Asb',
                           img_url='img/nba.jpg',
                           )

# google sign in
GOOGLE_OAUTH2_CLIENT_ID = '774374692298-jtj2he5qpci5mdblvaucvgolgastlo8t.apps.googleusercontent.com'

@app.route('/log_in')
def log_in():
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


# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)