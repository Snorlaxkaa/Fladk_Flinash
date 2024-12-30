# 匯入 Flask-WTF 表單擴展以及相關的類和驗證器
from flask_wtf import FlaskForm  # Flask-WTF 的核心類，用於創建表單
from flask_wtf.file import FileField, FileAllowed  # 用於處理文件上傳
from flask_login import current_user  # 獲取當前登入用戶
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField  # 定義表單欄位
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError  # 表單欄位的驗證器
from flaskblog.models import User  # 導入 User 模型，用於驗證數據

# 註冊用戶的表單
class RegistrationForm(FlaskForm):
    """
    註冊表單：
    - 用於新用戶的註冊，包含用戶名、電子郵件、密碼和確認密碼欄位。
    """
    username = StringField('Username',  # 用戶名欄位
                           validators=[DataRequired(), Length(min=2, max=20)])  # 必填，長度在 2 到 20 字元之間
    email = StringField('Email',  # 電子郵件欄位
                        validators=[DataRequired(), Email()])  # 必填，必須是有效的電子郵件格式
    password = PasswordField('Password', validators=[DataRequired()])  # 密碼欄位，必填
    confirm_password = PasswordField('Confirm Password',  # 確認密碼欄位
                                     validators=[DataRequired(), EqualTo('password')])  # 必填，需與密碼一致
    submit = SubmitField('Sign Up')  # 提交按鈕

    # 用戶名驗證器，檢查用戶名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()  # 查詢資料庫
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')  # 如果存在，拋出錯誤

    # 電子郵件驗證器，檢查電子郵件是否已被註冊
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()  # 查詢資料庫
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')  # 如果存在，拋出錯誤

# 用戶登入的表單
class LoginForm(FlaskForm):
    """
    登入表單：
    - 用於已註冊用戶的登入，包含電子郵件和密碼欄位。
    """
    email = StringField('Email',  # 電子郵件欄位
                        validators=[DataRequired(), Email()])  # 必填，必須是有效的電子郵件格式
    password = PasswordField('Password', validators=[DataRequired()])  # 密碼欄位，必填
    remember = BooleanField('Remember Me')  # 勾選框，用於記住用戶
    submit = SubmitField('Login')  # 提交按鈕

# 更新帳戶的表單
class UpdateAccountForm(FlaskForm):
    """
    更新帳戶表單：
    - 用於用戶更新帳戶資料，包括用戶名、電子郵件和頭像圖片。
    """
    username = StringField('Username',  # 用戶名欄位
                           validators=[DataRequired(), Length(min=2, max=20)])  # 必填，長度在 2 到 20 字元之間
    email = StringField('Email',  # 電子郵件欄位
                        validators=[DataRequired(), Email()])  # 必填，必須是有效的電子郵件格式
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])  # 頭像圖片欄位，只允許 jpg 和 png 格式
    submit = SubmitField('Update')  # 提交按鈕

    # 用戶名驗證器，檢查用戶名是否已存在
    def validate_username(self, username):
        if username.data != current_user.username:  # 確保只有修改後的用戶名才需要檢查
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')  # 如果存在，拋出錯誤

    # 電子郵件驗證器，檢查電子郵件是否已被註冊
    def validate_email(self, email):
        if email.data != current_user.email:  # 確保只有修改後的電子郵件才需要檢查
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')  # 如果存在，拋出錯誤

# 新增文章的表單
class PostForm(FlaskForm):
    """
    發表文章表單：
    - 用於用戶創建新文章，包含標題和內容欄位。
    """
    title = StringField('Title', validators=[DataRequired()])  # 標題欄位，必填
    content = TextAreaField('Content', validators=[DataRequired()])  # 內容欄位，必填
    submit = SubmitField('Post')  # 提交按鈕

# 發送密碼重置請求的表單
class RequestResetForm(FlaskForm):
    """
    密碼重置請求表單：
    - 用於用戶請求重置密碼，僅需提供電子郵件。
    """
    email = StringField('Email',  # 電子郵件欄位
                        validators=[DataRequired(), Email()])  # 必填，必須是有效的電子郵件格式
    submit = SubmitField('Request Password Reset')  # 提交按鈕

    # 電子郵件驗證器，檢查該電子郵件是否已註冊
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()  # 查詢資料庫
        if user is None:  # 如果電子郵件不存在
            raise ValidationError('There is no account with that email. You must register first.')  # 提示需要註冊

# 密碼重置的表單
class ResetPasswordForm(FlaskForm):
    """
    密碼重置表單：
    - 用於用戶重設密碼，包含新密碼和確認密碼欄位。
    """
    password = PasswordField('Password', validators=[DataRequired()])  # 新密碼欄位，必填
    confirm_password = PasswordField('Confirm Password',  # 確認密碼欄位
                                     validators=[DataRequired(), EqualTo('password')])  # 必填，需與新密碼一致
    submit = SubmitField('Reset Password')  # 提交按鈕
