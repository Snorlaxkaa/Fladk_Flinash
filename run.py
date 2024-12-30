# 從 flaskblog 模組中匯入 create_app 函式
from flaskblog import create_app

# 使用工廠模式創建 Flask 應用程式實例
app = create_app()

# 啟動應用程式
if __name__ == '__main__':
    # 啟動 Flask 開發伺服器，並啟用除錯模式（debug 模式方便開發時找錯誤）
    app.run(debug=True)
