from flask import Flask,render_template,url_for,redirect,request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import jsonify
import pymysql
 

app = Flask( 
    __name__,
    static_folder='static',
    static_url_path='/'
)

# 建立網站首頁的回應方式
@app.route("/")
def index(): # 用來回應網站首頁連線的函式
    return render_template('index.html') # 回應網站首頁的內容




# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)
