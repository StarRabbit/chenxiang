from . import db, login_manager
from flask_login import UserMixin,AnonymousUserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# 继承了db.Model后，该模型便具备了ORM的一系列方法//与scrapy的Item类似
# @网站权限设计：目前我们考虑以下几种用户角色：
# @1，网站管理员：拥有所有用户权利+封杀用户权利+修改用户声望权利
# @2，评判者用户（judger）：拥有短评数属性，审影数属性，声望值属性，筛选评论权利（给评论加权），给他人评分投票权，写长短影评权
# @3，初级用户（priuser）：拥有投票权，写短评权，短评数属性（积累50部后升级）
class BASEPERMISSION:
    FOLLOW = 0x01
    VOTE = 0x02
    SHORTCOMMENT = 0x04
    MARK = 0x08
class SENIORPERMISSION:
    MODERATE=0x10
    ARTICLE=0x20
    ADMINISTER=0x80


class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    # 用户注册时，default字段为True的角色会被设定为默认角色,index设定为True查询会更快
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)

    #通过此属性获得所有该role的用户对象，此表与users表之间的反向关系通过role属性去查找对应User
    #该属性并不会成为数据表中的一列
    users = db.relationship('User',backref='role',lazy='dynamic')

    # 这个静态方法用于在命令行中向数据库插入角色
    @staticmethod
    def insert_roles():
        # 角色字典
        roles = {
            'Primaryuser':(
                BASEPERMISSION.FOLLOW|
                BASEPERMISSION.SHORTCOMMENT|
                BASEPERMISSION.VOTE|
                BASEPERMISSION.MARK,True
            ),
            'Judger':(
                BASEPERMISSION.FOLLOW |
                BASEPERMISSION.SHORTCOMMENT |
                BASEPERMISSION.VOTE |
                BASEPERMISSION.MARK|
                SENIORPERMISSION.ARTICLE|
                SENIORPERMISSION.MODERATE,False
            ),
            'Administrator':(
                0xff,False
            )
            }
        for role_name in roles:
            # 这行代码将查询数据库中是否有我们角色字典中的角色
            #对字典进行遍历得到的只是字典的key
            role = Role.query.filter_by(name=role_name).first()
                # 如果没找到
            if  role is None:
                    # 这边需要注意一个问题，为什么这边没有__init__方法，
                    # 也能直接将role_name直接传进去初始化？这是因为db.model里面实现的功能
                role = Role(name=role_name)
                role.permissions = roles[role_name][0]
                role.default = roles[role_name][1]
                db.session.add(role)
        db.session.commit()

class Movie(db.Model):
    __tablename__ = 'douban_movie_profile'
    id = db.Column(db.Integer, primary_key=True)
    movie_title = db.Column(db.String(64))
    intro = db.Column(db.Text)
    credit = db.Column(db.Float)
    judge_crowd = db.Column(db.Integer)
    year = db.Column(db.Integer)
    img_src = db.Column(db.String(255))
    status = db.Column(db.String(5))
    comments = db.relationship('MovieComment',lazy='dynamic')


# 电影评论：包括标题、作者、电影链接与简介、评论、赞同数、反对数
class Review(db.Model):
    __tablename__ = 'reviews'
    #主键
    id = db.Column(db.Integer,primary_key=True)
    # 标题
    title = db.Column(db.String(128))
    # 内容
    text = db.Column(db.Text)
    #名字
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    #电影信息
    movie_id = db.Column(db.Integer, db.ForeignKey('douban_movie_profile.id'))
    # 时间信息
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #评论
    comments = db.relationship('ShortComment', lazy='dynamic')
#    赞同数
    up = db.Column(db.Integer)
#    反对数
    down = db.Column(db.Integer)


class MovieComment(db.Model):
    __tablename__ = 'movie_comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('douban_movie_profile.id'))
    credit = db.Column(db.Float)
    up = db.Column(db.Integer)
    down = db.Column(db.Integer)
    disabled = db.Column(db.Boolean)



class ShortComment(db.Model):
    __tablename__ = 'short_comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'))
    up = db.Column(db.Integer)
    down = db.Column(db.Integer)

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    # 表的主键
    id = db.Column(db.Integer,primary_key = True)
    # 这一列不允许出现重复的值
    email = db.Column(db.String(64),unique = True)
    # 这一列是用户名，不允许出现重复的值
    username = db.Column(db.String(64),unique=True,index = True)
    # 本张表的外键
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    # 数据库里存储的不是用户密码，而是其哈希加密值
    password_hash = db.Column(db.String(128))
    # 是否邮件认证过，防止机器人
    confirmed = db.Column(db.Boolean,default=False)
    # 马甲？
    name = db.Column(db.String(64))
    #评论
    short_comments = db.relationship('ShortComment', backref = 'author',lazy='dynamic')
    movie_comments = db.relationship('MovieComment', backref = 'author',lazy='dynamic')
    # 文章
    reviews = db.relationship('Review', backref = 'author',lazy='dynamic')


    # 用户时间信息
    last_seen = db.Column(db.DateTime(),default = datetime.utcnow())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SILENTWOOD_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # if self.email is not None and self.avatar_hash is None:
        #     self.avatar_hash = hashlib.md5(
        #         self.email.encode('utf-8')).hexdigest()
        # self.followed.append(Follow(followed=self))

    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions
    def is_admin(self):
        return self.can(SENIORPERMISSION.ADMINISTER)
    # 记录下最近登录的时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 生成具有一定时间限制的token
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm')!= self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 实现用户密码哈希储存及密码验证
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)


# 继承已经实现相关方法的AnonymousUserMixin类，为系统提供匿名类
class AnonymousUser(AnonymousUserMixin):
    # 这个方法是进行权限检查的方法，传入permission，检查用户是否具备permission
    def can(self,permission):
        return False

    # 检查是否是管理员
    def is_administrator(self):
        return False

# 不需要实例化
login_manager.anonymous_user = AnonymousUser

# 这个回调函数跟session操作有关，详细信息参考cookie与session相关资料
# 这是flask_login要求实现的一个callback
# 这里的get方法参数是primary key，也就是说这个user_id就是user表的id行。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


