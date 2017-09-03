import os
# 获取此app的目录路径，到上层文件夹，并转换为绝对路径（\）
basedir = os.path.abspath(os.path.dirname(__file__))

# 制作配置基类，记录通用配置信息。注：python3已经把旧类型去掉了，也就是说已经隐式继承了object，所以，python3中写不写继承object都是没有区别的
class Config:
    # 关于这个密钥的重要性，参见CSRF网络攻击和防御
    SECRET_KEY = os.environ.get('SECRET_KEY')or'a string for silentwood pass'
    # 数据库：每次请求结束后都会自动提交数据库的变动
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 邮箱服务配置：包括使用的邮箱服务器地址，端口配置，安全配置，邮箱账户配置等
    MAIL_SERVER = 'smtp.126.com'

    MAIL_PORT = 25
    #S1：这个邮箱问题很头疼，重新建立项目后解决，删除原项目文件失败，推测与硬件系统问题有关。
    # 这边要注意，折腾了很久，虽然原问题并没有解决，但是我们也有些经验
    # 经验：查bug一定要将debug模式打开，以便确定问题，前面我们出现的问题就是SSL出错的问题，这样的话我们就换TLS吧
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'bosonn@126.com'
    MAIL_PASSWORD = '520517boson'
    # 网站管理信息配置
    SILENTWOOD_MAIL_SUBJECT_PREFIX = '***沉香电影***'
    SILENTWOOD_MAIL_SENDER = 'bosonn@126.com'
    SILENTWOOD_ADMIN = os.environ.get('SILENTWOOD_ADMIN')
    SILENTWOOD_PER_PAGE_ITEM = 20

    # 这个静态方法的作用是对网站配置进行初始化，在我们的app中暂时留在这
    @staticmethod
    def init_app(app):
        pass
# 开发阶段的配置设定
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')or\
                           'mysql+pymysql://root:123456@localhost:3306/test_data'
# 测试阶段的配置
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')or\
        'mysql+pymysql://root:123456@localhost:3306/test_data'
# 正式运行阶段的配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
        'sqlite:///'+os.path.join(basedir,'data.sqlite')

# 配置字典，里面装着四个配置类，不需要实例化
# 使用时从外部引入这个字典，直接取出对应的配置类就行了
# 默认是开发配置
config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}