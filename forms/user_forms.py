from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, URLField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль',  validators=[DataRequired()])
    password_rep = PasswordField('Повторите пароль',  validators=[DataRequired()])
    avatar_image_url = URLField('URL аватарки (необезательно)')
    submit = SubmitField('Зарегестрироваться')
