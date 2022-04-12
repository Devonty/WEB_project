import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from .default import *

class RelationsGroupsUsers(SqlAlchemyBase):
    __tablename__ = 'relations_groups_users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    who = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    where = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))
    when = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
