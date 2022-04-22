from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, URLField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class CreateForm(FlaskForm):
    name = StringField('Название группы', validators=[DataRequired()])
    description = StringField('Описание')
    submit = SubmitField('Создать')