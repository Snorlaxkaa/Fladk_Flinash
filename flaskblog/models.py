from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


# 設置用戶加載函數，當 Flask-Login 需要加載當前登入的用戶時，會調用此函數
@login_manager.user_loader
def load_user(user_id):
    # 根據用戶的 ID 從資料庫中查詢用戶記錄
    return User.query.get(int(user_id))


# 用戶模型，用於存儲用戶的相關數據
class User(db.Model, UserMixin):
    # 用戶的唯一 ID，主鍵
    id = db.Column(db.Integer, primary_key=True)
    # 用戶名，必須唯一且不可為空，最大長度 20
    username = db.Column(db.String(20), unique=True, nullable=False)
    # 用戶的電子郵件，必須唯一且不可為空，最大長度 120
    email = db.Column(db.String(120), unique=True, nullable=False)
    # 用戶的頭像文件名，預設為 'default.jpg'
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    # 用戶的密碼，經加密後存儲，最大長度 60
    password = db.Column(db.String(60), nullable=False)
    # 與 Post 模型的關聯關係，用於表示用戶所創建的文章
    # `backref='author'` 創建一個屬性，讓文章可以反向訪問其作者
    # `lazy=True` 表示當訪問時才載入數據
    posts = db.relationship('Post', backref='author', lazy=True)

    # 定義物件的字串表示，用於調試或日誌中顯示用戶信息
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# 文章模型，用於存儲文章的相關數據
class Post(db.Model):
    # 文章的唯一 ID，主鍵
    id = db.Column(db.Integer, primary_key=True)
    # 文章的標題，不可為空，最大長度 100
    title = db.Column(db.String(100), nullable=False)
    # 文章的發布日期，預設為當前時間
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # 文章的內容，長度不限，必填
    content = db.Column(db.Text, nullable=False)
    # 外鍵，用於連接到對應的用戶（作者）
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 定義物件的字串表示，用於調試或日誌中顯示文章信息
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
