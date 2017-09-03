from flask import render_template,redirect,request,url_for,flash,current_app
from flask_login import login_user, logout_user, login_required,current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,RegistrationForm
from ..email import send_email
# from .. import mail
# from flask_mail import Mail,Message
# from .random_test import send_mail

from wsgiref import simple_server

# 用户在发起请求服务器端做出反应之前的准备工作，这个叫请求钩子，原理是Signals
# is_authenticated查询用户是否登录，登录返回True
# 首先每个req过来时Flask——login就已经拿出user_id并生成了current对象，这个方法只是对每个req做一些
# 进一步处理前必须要做的事情，比如记下访问时间等，与用户认证无关
@auth.before_app_request
def before_request():
    # 注意flask_login的实现，cookie中的user_id什么时候提取？如何提取？session如何工作？
    if current_user.is_authenticated:
        # 如果用户已经登录，则记录其登录信息并将其添加到数据库session（事务）中
        # 以准备数据库内容的更改
        current_user.ping()
        if not current_user.confirmed  and request.endpoint[:5]!='auth.' \
                and request.endpoint!='static':
            # 这个request是封装了用户请求信息的程序上下文，同样的上下文还有g，session，current_app
            # 这个endpoint是什么东西？

            # 如果用户登陆了但是没有通过邮箱认证并且访问了其他需要认证才能访问的页面，
            # 就将重定向到未认证页面。
            return redirect(url_for('auth.unconfirmed'))



@auth.route('/unconfirmed')
def unconfirmed():
    # 如果被重定向到这里的登录用户已经确认了，将会被发向首页，未确认用户只能看需要确认的页面（不合理，应该
    # 给一个主页链接给已注册登录但是没有邮件确认的用户）
    if current_user.is_anonymous or current_user.confirmed:
        # 如果用户只是游客或者误打误撞进来的用户，直接将其打发到主页
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    # 这边的原理还是不清楚，得好好弄明白
    # 猜测：通过请求方法判断是否submit，如果是submit就
    # 直接通过form.email取request中的数据，这边的form.email只是个形式
    # 实际是通过对象的字段获取对应request.form的数据
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        # 这里有一点要注意，本来通过数据库配置我们已经能在每次请求的结尾自动提交数据库变动
        # 也就是只要session.add就行了，这里为什么要commit呢？
        # 因为下面生成token必须要用到user的id,不提交的话数据库是不会生成用户id的
        db.session.commit()
        token = user.generate_confirmation_token()
        print(token)
        print(user.email)
        send_email(user.email,'请验证你的账号','auth/email/confirm.html',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        # url_for()函数的_external设置为true可以帮我们生成完整的url
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('confirm/<token>',methods=['GET'])
@login_required
# 用于已经注册但未确认的用户
def confirm(token):
    # 必须要确认一下哦，防止用户多次点击
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('通过验证！开始探索吧')
    else:
        flash('验证失败！请重新验证')
    return redirect(url_for('main.index'))


@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # 一个重要的函数，实际上是吧user_id设置成session
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next')or url_for('main.index'))
        flash('用户名或密码错误，请重新输入')
    # 注意，这边导致我烦了一个晚上，一定要注模板层级关系（路径），默认都是在templates下面，
    # 如果templates下面还有次级文件，一定要写清楚
    return render_template('auth/login.html',form=form)

@auth.route('/resend_confirmation',methods=['GET','POST'])
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '请验证你的账号', 'auth/email/confirm.html', user=current_user, token=token)
    flash('确认邮件已经重新发送.')
    return redirect(url_for('main.index'))

# 登出用户并且清除记住我cookie
@auth.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
