from flask import render_template, redirect,url_for, abort, flash, request,current_app,make_response
from flask_login import login_required,current_user
from . import main
from .. import db
from sqlalchemy import desc
# 妈的，找的我好苦（不对，是另一个地方）
from ..models import  Role, User,Movie
# from ..models

# 为main蓝图（可以将main看成是app的一个分身）写路由

# 第一：主页路由
@main.route('/',methods = ['GET','POST'])
# 主页应该包含哪些？如果没有登录，就先去认证页面
def index():
    # 首页从数据库取出按年份排名的电影
    # 首先拿到请求页数,这边的的args是ImmutableMultiDict
    page = request.args.get('page',1,type=int)
    # movie_list = Movie.query.order_by(desc(Movie.year)).all()
    # paginate对象拥有调用前一页、后一页，总页数等方法，它可以用来生成分页链接
    paginater = Movie.query.order_by(Movie.year).paginate(page=page,per_page=20,error_out=False)
    return render_template('index.html',paginater = paginater)


@main.route('/test',methods=['GET','POST'])
@login_required
def test():
    return 'Hello,World'

@main.route('/moderate',methods=['GET','POST'])
@login_required
def moderate():
    return 'Hello,World'
