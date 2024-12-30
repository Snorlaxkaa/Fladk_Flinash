from datetime import datetime  # 用於處理日期和時間
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # 用於生成和驗證安全令牌
from flask import current_app  # 獲取當前的 Flask 應用實例
from flaskblog import db, login_manager  # 導入資料庫和登入管理器
from flask_login import UserMixin  # 用於簡化用戶模型的登入功能

# 定義用戶加載器，Flask-Login 需要使用此函數加載用戶
@login_manager.user_loader
def load_user(user_id):
    """
    根據用戶 ID 加載用戶：
    - 當用戶登入後，Flask-Login 會調用此函數獲取用戶數據。
    - 返回對應的 User 模型實例。
    """
    return User.query.get(int(user_id))  # 根據用戶 ID 從資料庫中查詢用戶記錄

# 用戶模型
class User(db.Model, UserMixin):
    """
    User 類代表用戶表，每個屬性對應資料表中的一列。
    同時繼承 UserMixin，提供與用戶身份驗證相關的基本方法。
    """
    id = db.Column(db.Integer, primary_key=True)  # 用戶 ID，主鍵
    username = db.Column(db.String(20), unique=True, nullable=False)  # 用戶名，需唯一，不能為空
    email = db.Column(db.String(120), unique=True, nullable=False)  # 電子郵件，需唯一，不能為空
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # 用戶頭像，預設為 default.jpg
    password = db.Column(db.String(60), nullable=False)  # 用戶密碼，使用哈希加密後存儲
    posts = db.relationship('Post', backref='author', lazy=True)  # 用戶與文章的一對多關係

    def get_reset_token(self, expires_sec=1800):
        """
        生成重置密碼的安全令牌：
        - 使用 itsdangerous 庫生成令牌。
        - expires_sec 定義令牌的有效期（以秒為單位）。
        返回：
            - 生成的令牌（字串）。
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)  # 使用應用的密鑰初始化序列化器
        return s.dumps({'user_id': self.id}).decode('utf-8')  # 將用戶 ID 加入令牌並返回

    @staticmethod
    def verify_reset_token(token):
        """
        驗證重置密碼的安全令牌：
        - 從令牌中提取用戶 ID。
        - 如果令牌無效或過期，返回 None。
        返回：
            - 對應的 User 模型實例，或 None。
        """
        s = Serializer(current_app.config['SECRET_KEY'])  # 使用應用的密鑰初始化序列化器
        try:
            user_id = s.loads(token)['user_id']  # 嘗試解碼令牌並提取用戶 ID
        except:
            return None  # 如果解碼失敗或令牌無效，返回 None
        return User.query.get(user_id)  # 根據用戶 ID 查詢用戶記錄

    def __repr__(self):
        """
        定義用戶對象的打印格式，便於調試。
        """
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# 文章模型
class Post(db.Model):
    """
    Post 類代表文章表，每個屬性對應資料表中的一列。
    """
    id = db.Column(db.Integer, primary_key=True)  # 文章 ID，主鍵
    title = db.Column(db.String(100), nullable=False)  # 文章標題，不能為空
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 發布日期，默認為當前 UTC 時間
    content = db.Column(db.Text, nullable=False)  # 文章內容，不能為空
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 外鍵，連結到用戶表的 ID

    def __repr__(self):
        """
        定義文章對象的打印格式，便於調試。
        """
        return f"Post('{self.title}', '{self.date_posted}')"
