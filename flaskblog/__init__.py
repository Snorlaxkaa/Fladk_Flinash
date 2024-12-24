from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# 建立 Flask 應用程式的實例
app = Flask(__name__)

# 配置應用程式的秘密金鑰，用於保護表單數據的安全性，例如 CSRF 防護
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# 配置應用程式的資料庫 URI，這裡使用 SQLite 並將資料庫存儲於本地的 `site.db`
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# 初始化 SQLAlchemy，用於資料庫操作
db = SQLAlchemy(app)

# 初始化 Bcrypt，用於密碼加密和驗證
bcrypt = Bcrypt(app)

# 初始化 LoginManager，用於處理使用者登入狀態管理
login_manager = LoginManager(app)

# 配置登入的頁面路徑，當未登入的使用者嘗試訪問需要登入的頁面時，會被重定向到此頁面
login_manager.login_view = 'login'

# 配置閃現消息的分類，這裡設置為 'info' 類別，用於顯示登入相關的提示
login_manager.login_message_category = 'info'

# 導入路由模組（在最後導入以避免循環導入問題）
from flaskblog import routes
