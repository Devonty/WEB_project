import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from .default import *


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    register_datetime = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    avatar_image_url = sqlalchemy.Column(sqlalchemy.String, default=URL_DEFAULT_AVATAR)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    groups_id = sqlalchemy.Column(sqlalchemy.String, default='')
    admin_groups_id = sqlalchemy.Column(sqlalchemy.String, default='')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
