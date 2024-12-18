from flaskblog import app, db, User

# 推送應用上下文
with app.app_context():
    # 創建一個新的用戶
    new_user = User(username='testuser', email='test@example.com', password='password')
    db.session.add(new_user)
    db.session.commit()
    print("User added successfully!")
