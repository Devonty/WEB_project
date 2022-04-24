from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, URLField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

class CreatePost(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = StringField('Содержание', validators=[DataRequired()])
    image_url = StringField('Ссылка на картинку(URL)')
    submit = SubmitField('Запостить')
