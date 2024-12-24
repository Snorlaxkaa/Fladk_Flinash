from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

# 模擬的部落格文章數據（用於展示，實際應從資料庫中提取）
posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

# 路由: 主頁
@app.route("/")
@app.route("/home")
def home():
    # 渲染首頁模板並傳遞部落格文章數據
    return render_template('home.html', posts=posts)

# 路由: 關於頁面
@app.route("/about")
def about():
    # 渲染關於頁面模板，並傳遞頁面標題
    return render_template('about.html', title='About')

# 路由: 註冊頁面
@app.route("/register", methods=['GET', 'POST'])
def register():
    # 如果用戶已經登入，重定向到首頁
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # 初始化註冊表單
    form = RegistrationForm()
    
    # 檢查表單是否通過驗證
    if form.validate_on_submit():
        # 加密用戶輸入的密碼
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # 建立新用戶實例
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        # 將新用戶添加到資料庫並提交
        db.session.add(user)
        db.session.commit()
        
        # 使用閃現消息通知用戶註冊成功
        flash('Your account has been created! You are now able to log in', 'success')
        
        # 重定向到登入頁面
        return redirect(url_for('login'))
    
    # 渲染註冊頁面模板，傳遞表單和頁面標題
    return render_template('register.html', title='Register', form=form)

# 路由: 登入頁面
@app.route("/login", methods=['GET', 'POST'])
def login():
    # 如果用戶已經登入，重定向到首頁
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    # 初始化登入表單
    form = LoginForm()
    
    # 檢查表單是否通過驗證
    if form.validate_on_submit():
        # 根據電子郵件查詢用戶
        user = User.query.filter_by(email=form.email.data).first()
        
        # 檢查用戶是否存在以及密碼是否正確
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # 登入用戶並設置 "記住我" 功能
            login_user(user, remember=form.remember.data)
            
            # 如果用戶嘗試訪問受保護頁面，重定向到該頁面，否則重定向到首頁
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # 如果登入失敗，顯示錯誤消息
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    # 渲染登入頁面模板，傳遞表單和頁面標題
    return render_template('login.html', title='Login', form=form)

# 路由: 登出
@app.route("/logout")
def logout():
    # 登出當前用戶
    logout_user()
    # 重定向到首頁
    return redirect(url_for('home'))

# 路由: 帳戶頁面（需登入）
@app.route("/account")
@login_required
def account():
    # 渲染帳戶頁面模板，並傳遞頁面標題
    return render_template('account.html', title='Account')
