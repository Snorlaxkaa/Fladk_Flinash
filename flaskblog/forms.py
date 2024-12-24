from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


# 用於處理用戶註冊表單的類別
class RegistrationForm(FlaskForm):
    # 用戶名字段，需符合長度要求並且必填
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    
    # 電子郵件字段，需符合電子郵件格式並且必填
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    # 密碼字段，必填
    password = PasswordField('Password', validators=[DataRequired()])
    
    # 確認密碼字段，需與密碼字段匹配且必填
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    
    # 提交按鈕
    submit = SubmitField('Sign Up')

    # 自定義的用戶名驗證方法，檢查用戶名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    # 自定義的電子郵件驗證方法，檢查電子郵件是否已存在
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


# 用於處理用戶登入表單的類別
class LoginForm(FlaskForm):
    # 電子郵件字段，需符合電子郵件格式並且必填
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    # 密碼字段，必填
    password = PasswordField('Password', validators=[DataRequired()])
    
    # 記住我選項，供用戶選擇是否記住登入狀態
    remember = BooleanField('Remember Me')
    
    # 提交按鈕
    submit = SubmitField('Login')
