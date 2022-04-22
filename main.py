from flask import Flask, render_template, redirect
from data import db_session
from flask_login import LoginManager, current_user, logout_user, login_user, login_required

from data.default import *
from sqlalchemy.orm import lazyload, joinedload
from data.users import User
from data.group import Group
from data.posts import Post
from data.relations import RelationsGroupsUsersPosts, RelationsGroupUser

from forms import user_forms, group_forms

import logging

logger = logging.getLogger('WebForum')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.init_app(app)


def render_template_moded(*args, **kwargs):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        groups_id = [i.where_id for i in db_sess.query(RelationsGroupUser).filter(
            RelationsGroupUser.who_id == current_user.id)]
        groups_id_name = [(str(i.id), str(i.name)) for i in
                          db_sess.query(Group).filter(Group.id.in_(groups_id))]
        kwargs['groups_id_name'] = groups_id_name
        logger.info(groups_id_name)
        logger.info(groups_id)
    return render_template(*args, **kwargs)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    return render_template_moded('index.html', title='Главная страница')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = user_forms.RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_rep.data:
            return render_template_moded('register.html', title='Регистрация',
                                         form=form,
                                         message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template_moded('register.html', title='Регистрация',
                                         form=form,
                                         message="Такоя почта уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template_moded('register.html', title='Регистрация',
                                         form=form,
                                         message="Такое имя пользователя уже есть")
        avatar_url = form.avatar_image_url.data if \
            form.avatar_image_url.data else URL_DEFAULT_AVATAR
        user = User(
            name=form.name.data,
            email=form.email.data,
            avatar_image_url=avatar_url
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template_moded('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = user_forms.LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template_moded('login.html',
                                     message="Неправильный логин или пароль",
                                     form=form)
    return render_template_moded('login.html', title='Авторизация', form=form)


@app.route('/group/<group_id>')
@login_required
def group_page(group_id):
    db_sess = db_session.create_session()
    if not db_sess.query(RelationsGroupUser).filter(RelationsGroupUser.who_id == current_user.id,
                                                    RelationsGroupUser.where_id == group_id).first():
        # Хочет ли вступить в группу
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        return render_template_moded('join_group.html', group=group)

    group_content = db_sess.query(RelationsGroupsUsersPosts).filter(
        RelationsGroupsUsersPosts.where_id == group_id).all()
    posts_id = list(map(lambda x: x.what_id, group_content))
    posts = db_sess.query(Post).filter(Post.id.in_(posts_id)).all()
    return render_template_moded('group_page.html', posts=posts)


@app.route('/create_group', methods=['POST', 'GET'])
@login_required
def create_group():
    form = group_forms.CreateForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.name == form.name.data).first()
        if group:
            return render_template_moded('create_group.html',
                                         title='Создание группы',
                                         message='Имя уже занято!',
                                         form=form)

        local = db_sess.merge(current_user)
        # Создаю новую группу
        gr = Group(
            name=form.name.data,
            admin=local,
            admin_id=local.id,
            description=form.description.data
        )
        # Добавляю в базу
        db_sess.add(gr)
        db_sess.commit()
        # Ищу ее дополненую в базе, что бы ей присвоился id
        gr = db_sess.query(Group).filter(Group.name == gr.name).first()
        # Создаю связь Пользователь-Группа
        rel = RelationsGroupUser(
            who_id=current_user.id,
            where_id=gr.id
        )
        db_sess.add(rel)
        db_sess.commit()
        logger.debug('Создал связь и группу')
        return redirect('/index')

    return render_template_moded('create_group.html',
                                 title='Создание группы',
                                 form=form)

@app.route('/join_group/<group_id>')
@login_required
def join_group(group_id):
    db_sess = db_session.create_session()
    gr = db_sess.query(Group).filter(Group.id == group_id).first()
    rel = RelationsGroupUser(
        who_id=current_user.id,
        where_id=gr.id
    )
    db_sess.add(rel)
    db_sess.commit()
    logger.debug('Добавил связь')
    return redirect('/index')

@app.route('/leave_group/<group_id>')
@login_required
def leave_group(group_id):
    db_sess = db_session.create_session()
    connect = db_sess.query(RelationsGroupUser).filter(
        RelationsGroupUser.who_id == current_user.id,
        RelationsGroupUser.where_id == group_id
    )
    if connect:
        logger.debug(connect)
        db_sess.delete(connect)
        db_sess.commit()
    return redirect('/index')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/index")

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/register')

def main():
    db_session.global_init("db/base.db")
    db_sess = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
