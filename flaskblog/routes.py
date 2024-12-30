# 匯入必要的模組和函式，包括操作系統處理、隨機工具、圖片處理，以及 Flask 和相關擴展功能
import os  # 用於處理檔案路徑
import secrets  # 用於生成隨機字串，增強安全性
from PIL import Image  # 用於處理圖片
from flask import render_template, url_for, flash, redirect, request, abort  # Flask 核心功能
from flaskblog import app, db, bcrypt, mail  # 專案中的應用、資料庫加密工具和郵件功能
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,  # 導入表單類，用於處理用戶輸入
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post  # 導入資料庫模型，用於操作用戶與文章數據
from flask_login import login_user, current_user, logout_user, login_required  # 處理用戶登入、登出及驗證功能
from flask_mail import Message  # 用於發送電子郵件

# 首頁的路由
@app.route("/")
@app.route("/home")
def home():
    """
    首頁功能：顯示所有文章，按日期排序，支援分頁。
    如果有多頁文章，用戶可以通過網址參數 ?page= 頁碼來翻頁。
    """
    page = request.args.get('page', 1, type=int)  # 獲取當前頁碼，默認為第 1 頁
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)  # 按日期降序排列，分頁顯示
    return render_template('home.html', posts=posts)  # 將文章資料傳遞給模板渲染

# 關於頁面的路由
@app.route("/about")
def about():
    """
    關於頁面：展示靜態內容，介紹網站的信息。
    """
    return render_template('about.html', title='About')  # 加載 about.html 並傳遞標題資訊

# 註冊用戶功能的路由
@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    註冊新用戶功能：
    - 如果用戶已登入，直接跳轉到首頁。
    - 否則，顯示註冊表單，處理註冊邏輯。
    """
    if current_user.is_authenticated:  # 如果用戶已登入
        return redirect(url_for('home'))  # 跳轉到首頁
    form = RegistrationForm()  # 創建註冊表單實例
    if form.validate_on_submit():  # 當表單提交並通過驗證時
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # 哈希加密密碼
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)  # 創建新用戶
        db.session.add(user)  # 添加用戶到資料庫
        db.session.commit()  # 提交變更
        flash('您的帳號已創建成功！您現在可以登入了', 'success')  # 顯示成功提示
        return redirect(url_for('login'))  # 跳轉到登入頁面
    return render_template('register.html', title='Register', form=form)  # 渲染註冊頁面

# 登入功能的路由
@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    用戶登入功能：
    - 如果已登入，跳轉到首頁。
    - 否則，處理登入表單，檢查帳號與密碼，完成登入邏輯。
    """
    if current_user.is_authenticated:  # 如果用戶已登入
        return redirect(url_for('home'))  # 跳轉到首頁
    form = LoginForm()  # 創建登入表單實例
    if form.validate_on_submit():  # 當表單提交並通過驗證時
        user = User.query.filter_by(email=form.email.data).first()  # 查詢用戶
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # 驗證密碼是否正確
            login_user(user, remember=form.remember.data)  # 登入用戶並記住選項
            next_page = request.args.get('next')  # 獲取用戶試圖訪問的下一頁（如果有）
            return redirect(next_page) if next_page else redirect(url_for('home'))  # 跳轉到下一頁或首頁
        else:
            flash('登入失敗，請檢查您的電子郵件和密碼是否正確', 'danger')  # 顯示錯誤提示
    return render_template('login.html', title='Login', form=form)  # 渲染登入頁面

# 用戶登出的路由
@app.route("/logout")
def logout():
    """
    登出功能：登出當前用戶並跳轉到首頁。
    """
    logout_user()  # 登出當前用戶
    return redirect(url_for('home'))  # 跳轉到首頁

# 保存用戶上傳的頭像圖片
def save_picture(form_picture):
    """
    功能：處理用戶上傳的頭像圖片，調整大小並存儲到指定路徑。
    參數：
        form_picture - 用戶上傳的圖片文件
    返回：
        新生成的文件名
    """
    random_hex = secrets.token_hex(8)  # 生成隨機的 16 進制文件名
    _, f_ext = os.path.splitext(form_picture.filename)  # 獲取圖片的副檔名
    picture_fn = random_hex + f_ext  # 拼接新文件名
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)  # 設定存儲路徑

    output_size = (125, 125)  # 設定圖片的輸出大小
    i = Image.open(form_picture)  # 打開上傳的圖片
    i.thumbnail(output_size)  # 調整圖片尺寸
    i.save(picture_path)  # 保存圖片到指定路徑

    return picture_fn  # 返回新文件名

# 用戶帳戶管理頁面的路由
@app.route("/account", methods=['GET', 'POST'])
@login_required  # 此功能需要用戶登入才能訪問
def account():
    """
    用戶帳戶管理功能：
    - 顯示和編輯帳戶資訊（用戶名、電子郵件、頭像）。
    - 當表單提交時，更新用戶資訊。
    """
    form = UpdateAccountForm()  # 創建更新帳戶表單
    if form.validate_on_submit():  # 當表單提交並通過驗證時
        if form.picture.data:  # 如果有上傳新頭像
            picture_file = save_picture(form.picture.data)  # 保存新頭像
            current_user.image_file = picture_file  # 更新用戶的頭像路徑
        current_user.username = form.username.data  # 更新用戶名
        current_user.email = form.email.data  # 更新電子郵件
        db.session.commit()  # 提交變更
        flash('您的帳戶資訊已更新！', 'success')  # 顯示成功提示
        return redirect(url_for('account'))  # 重新加載頁面
    elif request.method == 'GET':  # 如果是 GET 請求，預填表單資料
        form.username.data = current_user.username  # 填入當前用戶名
        form.email.data = current_user.email  # 填入當前電子郵件
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)  # 獲取頭像路徑
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)  # 渲染帳戶管理頁面


# 新增文章的路由
@app.route("/post/new", methods=['GET', 'POST'])
@login_required  # 需要用戶登入才能訪問
def new_post():
    """
    創建新文章功能：
    - 用戶可以通過表單提交標題和內容，然後將文章保存到資料庫。
    """
    form = PostForm()  # 創建文章表單
    if form.validate_on_submit():  # 如果表單提交且驗證通過
        post = Post(title=form.title.data, content=form.content.data, author=current_user)  # 創建新文章
        db.session.add(post)  # 將文章添加到資料庫
        db.session.commit()  # 提交變更
        flash('您的文章已創建成功！', 'success')  # 顯示成功提示
        return redirect(url_for('home'))  # 跳轉到首頁
    return render_template('create_post.html', title='New Post',  # 渲染文章創建頁面
                           form=form, legend='New Post')

# 查看單篇文章的路由
@app.route("/post/<int:post_id>")
def post(post_id):
    """
    顯示單篇文章內容：
    - 根據文章 ID 從資料庫中查詢文章並展示內容。
    """
    post = Post.query.get_or_404(post_id)  # 如果找不到文章則返回 404 錯誤
    return render_template('post.html', title=post.title, post=post)  # 渲染文章內容頁面

# 更新文章的路由
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """
    更新文章功能：
    - 用戶可以編輯自己創建的文章，其他用戶無法訪問。
    """
    post = Post.query.get_or_404(post_id)  # 根據 ID 查詢文章
    if post.author != current_user:  # 確保只有作者可以編輯文章
        abort(403)  # 返回 403 禁止訪問錯誤
    form = PostForm()  # 創建文章表單
    if form.validate_on_submit():  # 如果表單提交且驗證通過
        post.title = form.title.data  # 更新文章標題
        post.content = form.content.data  # 更新文章內容
        db.session.commit()  # 提交變更
        flash('您的文章已更新！', 'success')  # 顯示成功提示
        return redirect(url_for('post', post_id=post.id))  # 跳轉到文章頁面
    elif request.method == 'GET':  # 如果是 GET 請求，預填表單數據
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',  # 渲染文章編輯頁面
                           form=form, legend='Update Post')

# 刪除文章的路由
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    """
    刪除文章功能：
    - 用戶只能刪除自己創建的文章。
    """
    post = Post.query.get_or_404(post_id)  # 根據 ID 查詢文章
    if post.author != current_user:  # 確保只有作者可以刪除文章
        abort(403)  # 返回 403 禁止訪問錯誤
    db.session.delete(post)  # 從資料庫刪除文章
    db.session.commit()  # 提交變更
    flash('您的文章已成功刪除！', 'success')  # 顯示成功提示
    return redirect(url_for('home'))  # 跳轉到首頁

# 查看特定用戶的所有文章
@app.route("/user/<string:username>")
def user_posts(username):
    """
    顯示某位用戶的所有文章：
    - 用戶可以通過網址訪問指定用戶的文章列表。
    - 支援分頁功能，每頁顯示固定數量的文章（例如 5 篇）。
    """
    # 從請求參數中取得當前頁碼，如果未提供則默認為第 1 頁
    page = request.args.get('page', 1, type=int)

    # 根據用戶名查詢對應的用戶資料，若不存在則返回 404 頁面
    user = User.query.filter_by(username=username).first_or_404()

    # 查詢該用戶創建的所有文章
    posts = (
        Post.query.filter_by(author=user)  # 篩選出該用戶的文章
        .order_by(Post.date_posted.desc())  # 按照發布日期降序排列，最近的文章在前
        .paginate(page=page, per_page=5)  # 實現分頁，每頁顯示 5 篇文章
    )

    # 渲染用戶文章列表頁面，並傳遞文章和用戶資料到模板
    return render_template('user_posts.html', posts=posts, user=user)

# 發送密碼重設郵件
def send_reset_email(user):
    """
    發送密碼重設請求的電子郵件：
    - 使用用戶的重設 token 生成重設密碼的鏈接，並通過郵件發送。
    """
    token = user.get_reset_token()  # 獲取用戶的重設 token
    msg = Message('Password Reset Request',  # 設置郵件標題
                  sender='johnny941114@gmail.com',  # 發件人
                  recipients=[user.email])  # 收件人
    msg.body = f'''要重設您的密碼，請點擊以下鏈接：
{url_for('reset_token', token=token, _external=True)}

如果您未發起此請求，請忽略此郵件，您的帳戶不會受到影響。
'''  # 郵件正文
    mail.send(msg)  # 發送郵件

# 提交密碼重設請求的路由
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """
    密碼重設請求功能：
    - 未登入用戶可以提交電子郵件請求重設密碼。
    """
    if current_user.is_authenticated:  # 如果用戶已登入，則跳轉到首頁
        return redirect(url_for('home'))
    form = RequestResetForm()  # 創建重設請求表單
    if form.validate_on_submit():  # 如果表單提交且驗證通過
        user = User.query.filter_by(email=form.email.data).first()  # 根據電子郵件查詢用戶
        send_reset_email(user)  # 發送重設郵件
        flash('已發送包含重設密碼指引的郵件到您的電子郵件！', 'info')  # 顯示提示信息
        return redirect(url_for('login'))  # 跳轉到登入頁面
    return render_template('reset_request.html', title='Reset Password', form=form)  # 渲染重設請求頁面

# 使用 token 進行密碼重設的路由
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """
    密碼重設功能：
    - 用戶通過電子郵件中的鏈接進行密碼重設。
    - 如果 token 無效或過期，則提示錯誤信息。
    """
    if current_user.is_authenticated:  # 如果用戶已登入，則跳轉到首頁
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)  # 驗證 token 的有效性
    if user is None:  # 如果 token 無效或過期
        flash('該鏈接無效或已過期', 'warning')  # 顯示警告信息
        return redirect(url_for('reset_request'))  # 跳轉到重設請求頁面
    form = ResetPasswordForm()  # 創建重設密碼表單
    if form.validate_on_submit():  # 如果表單提交且驗證通過
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # 哈希加密新密碼
        user.password = hashed_password  # 更新用戶密碼
        db.session.commit()  # 提交變更
        flash('您的密碼已更新！您現在可以登入了', 'success')  # 顯示成功提示
        return redirect(url_for('login'))  # 跳轉到登入頁面
    return render_template('reset_token.html', title='Reset Password', form=form)  # 渲染重設密碼頁面
