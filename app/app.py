import os
import sys
import datetime
from functools import wraps

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

db = SQLAlchemy()


# 数据库模型
class VisitStatistics(db.Model):
    __tablename__ = 'visit_statistics'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    times = db.Column(db.INTEGER, default=1)


class CommentStatistics(db.Model):
    __tablename__ = 'comment_statistics'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    times = db.Column(db.INTEGER, default=1)


class LikeStatistics(db.Model):
    __tablename__ = 'like_statistics'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    times = db.Column(db.INTEGER, default=1)


def statistic_traffic(db, obj):
    """
    网站今日访问量、评论量、点赞量统计装饰器
    :param db: 数据库操作对象
    :param obj: 统计模型类别(VisitStatistics,CommentStatistics,LikeStatistics)
    :return:
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            td = datetime.date.today()
            vst = obj.query.filter_by(date=td).first()
            if vst is None:
                new_vst = obj(date=td, times=1)
                db.session.add(new_vst)
            else:
                vst.times += 1
            db.session.commit()
            return func(*args, **kwargs)
        return decorated_function
    return decorator


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(basedir, 'data-dev.db')

db.init_app(app)
db.create_all(app=app)

date = datetime.date.today()


def get_data():
    vst = VisitStatistics.query.filter_by(date=date).first()
    cmt = CommentStatistics.query.filter_by(date=date).first()
    love = LikeStatistics.query.filter_by(date=date).first()
    if vst is None:
        visits = 0
    else:
        visits = vst.times
    if cmt is None:
        comments = 0
    else:
        comments = cmt.times
    if love is None:
        likes = 0
    else:
        likes = love.times
    return comments, likes, visits


@app.route('/')
@statistic_traffic(db, VisitStatistics)
def index():
    comments, likes, visits = get_data()
    return render_template("index.html", date=date, visits=visits, comments=comments, likes=likes)


@app.route('/comment/')
@statistic_traffic(db, CommentStatistics)
def comment():
    comments, likes, visits = get_data()
    return render_template("index.html", date=date, visits=visits, comments=comments, likes=likes)


@app.route('/like/')
@statistic_traffic(db, LikeStatistics)
def like():
    comments, likes, visits = get_data()
    return render_template("index.html", date=date, visits=visits, comments=comments, likes=likes)


if __name__ == '__main__':
    app.run(debug=True)

