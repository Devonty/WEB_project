import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from .default import *

from data.users import User
from data.group import Group
from data.posts import Post


class RelationsGroupsUsersPosts(SqlAlchemyBase):
    '''
    Таблица принадлежности постов к группам с авторами
    '''
    __tablename__ = 'relations_GUP'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    who_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    where_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))
    what_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    when = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())


class RelationsGroupUser(SqlAlchemyBase):
    '''
    Таблица принадлежности учатников к группам
    '''
    __tablename__ = 'relation_GU'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    who_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    where_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))
    when = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
