from flask import Flask,render_template,url_for,redirect,request
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
    return render_template('hot_package.html')

@app.route("/log_in")
def log_in():
    return render_template('log_in.html')

@app.route("/register")
def register():
    return render_template('register.html')

# 啟動網站伺服器
if __name__ == '__main__':
    app.run(debug=True)