from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_pagedown import PageDown
from config import config


# app扩展类的初始化，在后面我们将app传入其init_app函数进行初始化--也就是设置一些app属性配置
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
# 关于用户登录的重要模块
login_manager = LoginManager()
login_manager.session_protection = 'strong'
# 设置登录页面，当未登录时显示这个页面
login_manager.login_view = 'auth.login'
login_manager.login_message = '往来谈笑先拜帖~'

# 此工厂函数创建程序实例，并对其进行初始配置
def create_app(config_name):
    app = Flask(__name__)
    # 为app的config属性赋予一个config对象(实际上是从参数对象中取出值赋给已有的config对象)
    app.config.from_object(config[config_name])
    # 这是通过config对象对app进行初始化，当然，我们在这里并没有对其做真正的处理，只是留作一个接口
    config[config_name].init_app(app)

    # 对app进行初始化：前端插件，邮件插件，时间管理插件（不一定要，可以自己实现），数据库插件，用户认证插件
    # （其实也可以自己实现）
    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # mail=Mail(app)
#     注册蓝图，蓝图是分模块保存路由的对象，将创建好的蓝图注册到程序中，在蓝图中定义的路由才能起作用
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix = '/auth')
    return app
