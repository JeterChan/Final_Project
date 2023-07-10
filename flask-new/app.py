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

@app.route("/newest")
def newest():
    return render_template('newest.html')

@app.route("/hot")
def hot():
    return render_template('hot.html')

@app.route("/recommendation")
def recommendation():
    return render_template('recommendation.html')

@app.route("/collection")
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
