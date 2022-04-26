from flask import Flask, render_template, redirect, url_for, request
from data import db_session
from flask_login import LoginManager, current_user, logout_user, login_user, login_required

from sqlalchemy.orm import lazyload, joinedload

from data.default import *
from data.users import User
from data.group import Group
from data.posts import Post
from data.relations import RelationsGroupsUsersPosts, RelationsGroupUser

from forms import user_forms, group_forms, post_forms

import logging
import random

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
    # NOT_DEFINDED
    kwargs['NOT_DEFINDED'] = NOT_DEFINDED
    # CSS
    css_url = url_for('static', filename='css/style.css')
    kwargs['css_url'] = css_url
    # SCRIPT
    script_url = url_for('static', filename='js/script.js')
    kwargs['script_url'] = script_url
    # GROUPS
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        groups_id = [i.where_id for i in db_sess.query(RelationsGroupUser).filter(
            RelationsGroupUser.who_id == current_user.id)]
        groups = db_sess.query(Group).filter(Group.id.in_(groups_id)).all()
        groups_id_name = [(str(i.id), str(i.name)) for i in groups]
        kwargs['groups_id_name'] = groups_id_name
        kwargs['groups'] = groups
    logger.info(kwargs)
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
    if current_user.is_authenticated:
        return redirect('/index')

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
    if current_user.is_authenticated:
        return redirect('/index')

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
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if not group:
        return redirect('/index')
    if not db_sess.query(RelationsGroupUser).filter(RelationsGroupUser.who_id == current_user.id,
                                                    RelationsGroupUser.where_id == group_id).first():
        # Хочет ли вступить в группу
        return render_template_moded('join_group.html', group=group)

    group_content = db_sess.query(RelationsGroupsUsersPosts).filter(
        RelationsGroupsUsersPosts.where_id == group_id).all()
    posts_id = list(map(lambda x: x.what_id, group_content))
    posts = db_sess.query(Post).filter(Post.id.in_(posts_id)).all()
    return render_template_moded('group_page.html', posts=posts, group=group)


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
    # Проверка, что еще не участник
    connect = db_sess.query(RelationsGroupUser).filter(
        RelationsGroupUser.who_id == current_user.id,
        RelationsGroupUser.where_id == group_id
    ).first()
    group = db_sess.query(Group).filter(Group.id == group_id).first()

    print(group)
    if not group:
        return redirect('/index')
    if connect:
        return redirect(f'/group/{group_id}')
    logger.debug(f'Добавляю в группу {group_id} пользлователя {current_user.id}')
    # Добавление
    relation = RelationsGroupUser(
        who_id=current_user.id,
        where_id=group.id
    )
    db_sess.add(relation)
    db_sess.commit()
    logger.debug('Добавил связь')
    return redirect(f'/group/{group_id}')


@app.route('/leave_group/<group_id>')
@login_required
def leave_group(group_id):
    # Проверка, что участник
    db_sess = db_session.create_session()
    connect = db_sess.query(RelationsGroupUser).filter(
        RelationsGroupUser.who_id == current_user.id,
        RelationsGroupUser.where_id == group_id
    ).first()
    group = db_sess.query(Group).filter(Group.id == group_id).first()
    if not group or not connect:
        return redirect('/index')
    # Если был админом
    new_admin = random.choice(db_sess.query(User).all())
    group.admin_id = new_admin.id
    group.admin = new_admin

    db_sess.merge(group)
    db_sess.delete(connect)
    db_sess.commit()
    return redirect('/index')


@app.route('/create_post/<group_id>', methods=['POST', 'GET'])
@login_required
def create_post(group_id):
    # Проверка, что участник
    db_sess = db_session.create_session()
    connect = db_sess.query(RelationsGroupUser).filter(
        RelationsGroupUser.who_id == current_user.id,
        RelationsGroupUser.where_id == group_id
    ).first()
    logger.debug(connect)
    if not connect:
        return redirect("/index")

    # Обрабботка формы
    form = post_forms.CreatePost()
    if form.validate_on_submit():
        local = db_sess.merge(current_user)
        image_url = form.image_url.data if form.image_url.data else NOT_DEFINDED
        post = Post(
            author=local,
            author_id=local.id,
            title=form.title.data,
            text=form.text.data,
            image_url=image_url,
        )
        a = db_sess.add(post)
        logger.info(a)
        # Пытаюсь найти пост с присвоенным id
        posts = db_sess.query(Post).filter(
            Post.author == local,
            Post.author_id == local.id,
            Post.title == form.title.data,
            Post.text == form.text.data,
            Post.image_url == image_url,
        ).all()

        posts.sort(key=lambda x: x.post_datetime)
        post = posts[-1]

        rel = RelationsGroupsUsersPosts(
            who_id=local.id,
            where_id=group_id,
            what_id=post.id
        )
        db_sess.add(rel)
        db_sess.commit()
        return redirect(f'/group/{group_id}')
    return render_template_moded('create_post.html', form=form)


@app.route('/edit_post/<group_id>/<post_id>', methods=['POST', 'GET'])
@login_required
def edit_post(group_id, post_id):
    form = post_forms.CreatePost()
    if request.method == "GET":
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id == group_id).first()
        post = db_sess.query(Post).filter(Post.id == post_id).first()
        connect_GU = db_sess.query(RelationsGroupUser).filter(
            RelationsGroupUser.who_id == current_user.id,
            RelationsGroupUser.where_id == group_id
        ).first()
        connect_GUP = db_sess.query(RelationsGroupsUsersPosts).filter(
            RelationsGroupsUsersPosts.who_id == current_user.id,
            RelationsGroupsUsersPosts.where_id == group_id,
            RelationsGroupsUsersPosts.what_id == post_id
        ).first()

        # Если нет чего-либо
        if not all([group, post, connect_GU, connect_GUP]):
            return redirect("/index")

        logger.debug(connect_GU)
        # Если ли право редактировать (только у автора поста)
        if not current_user.id == post.author_id:
            return redirect(f"/group/{group_id}")

        form.title.data = post.title
        form.text.data = post.text
        form.image_url.data = post.image_url

    # Обрабботка формы
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == post_id).first()
        post.title = form.title.data
        post.text = form.text.data
        post.image_url = form.image_url.data
        db_sess.merge(post)
        db_sess.commit()
        return redirect(f'/group/{group_id}')
    return render_template_moded('create_post.html', form=form)


@app.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    db_sess = db_session.create_session()
    connect = db_sess.query(RelationsGroupsUsersPosts).filter(
        RelationsGroupsUsersPosts.what_id == post_id
    ).first()
    if not connect:
        return redirect('/index')

    post = db_sess.query(Post).filter(Post.id == connect.what_id).first()
    group = db_sess.query(Group).filter(Group.id == connect.where_id).first()
    author_id = connect.who_id
    if not post or not group:
        return redirect('/index')

    # Если не админ или автор поста
    if author_id != current_user.id and group.admin_id != current_user.id:
        return redirect('/index')

    db_sess.delete(post)
    db_sess.delete(connect)
    db_sess.commit()
    return redirect(f'/group/{group.id}')


@app.route('/post/<post_id>')
@login_required
def show_post(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    group_id = db_sess.query(RelationsGroupsUsersPosts).filter(
        RelationsGroupsUsersPosts.what_id == post_id
    ).first().where_id
    connect = db_sess.query(RelationsGroupUser).filter(
        RelationsGroupUser.where_id == group_id,
        RelationsGroupUser.who_id == current_user.id
    )
    # Если не в группе
    if not post or not connect:
        return redirect('/index')

    return render_template_moded('show_post.html', post=post)


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
