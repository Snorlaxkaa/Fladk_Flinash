import os  # 匯入 os 模組，用於獲取環境變數

# 定義應用程式的配置類

class Config:
    """
    配置類：
    - 用於存儲 Flask 應用的設定。
    - 包括安全密鑰、資料庫配置和電子郵件服務配置等。
    """
    # 應用的安全密鑰，用於防範跨站請求偽造（CSRF）和數據簽名等安全功能
    # 通過環境變數 'SECRET_KEY' 獲取，增加敏感信息的安全性
    SECRET_KEY = os.environ.get('SECRET_KEY')  

    # 資料庫的 URI（統一資源識別碼），用於連接資料庫
    # 通過環境變數 'SQLALCHEMY_DATABASE_URI' 獲取
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')  

    # 電子郵件服務配置：
    # 使用 Google 的 SMTP 伺服器發送郵件
    MAIL_SERVER = 'smtp.googlemail.com'  # 設置郵件伺服器的地址
    MAIL_PORT = 587  # 設置伺服器的端口，587 是支援 TLS 的端口
    MAIL_USE_TLS = True  # 啟用傳輸層安全性（TLS）協議
    MAIL_USERNAME = os.environ.get('EMAIL_USER')  # 通過環境變數獲取郵件服務的用戶名
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # 通過環境變數獲取郵件服務的密碼
