from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

# 这两张张表显示在未登录/未注册用户的主页上
class LoginForm(Form):
    email = StringField('电子邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('密码',validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')
# 这里要注意输入框的要求
class RegistrationForm(Form):
    email = StringField('电子邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('用户名',validators=[DataRequired(),Length(1,40),Regexp('[A-Za-z][A-Za-z0-9._]*$',0,\
                                             '只能包括字母数字下划线！')])
    password = PasswordField('密码', validators=[DataRequired()])
    password_confirm = PasswordField('请确认密码',validators = [DataRequired(),\
                                                           EqualTo('password',message='前后密码需相同')])
    submit = SubmitField('注册')
    protocol = BooleanField('我同意网站协议',default='checked')

    #自定义验证函数：以validate_开头，而且后面带着字段名，如果有那就和普通的验证函数（上面的validators，其实就是一堆callable）一起调用，可以raise error
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在，换个试试？')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')