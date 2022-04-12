import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from .default import *


class Group(SqlAlchemyBase):
    __tablename__ = 'groups'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    create_datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    member_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    admin = orm.relation('User')
    admin_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

