from flask import Flask
from data import db_session

from data.users import User
from data.group import Group
from data.posts import Post
from data.relations_groups_users import RelationsGroupsUsers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/index', methods=['GET'])
def index():
    pass


def main():
    db_session.global_init("db/base.db")
    db_sess = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
