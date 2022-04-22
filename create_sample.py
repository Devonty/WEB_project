from flask import Flask, render_template, redirect
from data import db_session
from flask_login import LoginManager, current_user, logout_user, login_user, login_required

from data.default import *

from data.users import User
from data.group import Group
from data.posts import Post
from data.relations import RelationsGroupsUsersPosts, RelationsGroupUser

from forms import user_forms


db_session.global_init("db/base.db")
db_sess = db_session.create_session()

DELETE = True
GROUP = True
POST = True
SPAM_POST = True

admin = db_sess.query(User).filter(User.id == 1).first()


if DELETE:
    db_sess.query(Group).delete()
    db_sess.query(RelationsGroupUser).delete()
    db_sess.query(RelationsGroupsUsersPosts).delete()
    db_sess.query(Post).delete()
for j in range(1, 2 + 1):
    if GROUP:

        gr = Group(
            name=f'First{j}',
            admin=admin,
            admin_id=admin.id,
            description='Описание'
        )
        db_sess.add(gr)

        gr = db_sess.query(Group).filter(Group.name == gr.name).first()
        rel = RelationsGroupUser(
            who_id=admin.id,
            where_id=gr.id
        )
        db_sess.add(rel)
    if SPAM_POST:
        group = db_sess.query(Group).filter(Group.id == j).first()
        for i in range(10):
            post_ = Post(
                author=admin,
                author_id=admin.id,
                title=f'Заголовок {i}',
                text=f'Группа {group.name}',
            )
            admin.posts.append(post_)
            db_sess.merge(admin)
            db_sess.add(post_)

            relation_ = RelationsGroupsUsersPosts(
                who_id=admin.id,
                where_id=group.id,
                what_id=post_.id,
            )
            db_sess.add(relation_)
db_sess.commit()