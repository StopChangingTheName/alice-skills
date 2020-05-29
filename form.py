from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, length


class AnswQuest(FlaskForm):
    question = TextAreaField('Формулировка вопроса', validators=[DataRequired(), length(max=200)])
    answer = StringField('Ответ на Ваш вопрос', validators=[DataRequired()])
    submit = SubmitField('Отправить')