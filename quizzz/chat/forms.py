from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    text = StringField('Username', validators=[
            DataRequired(message="Message must not be empty."),
            Length(max=1000, message='Message cannot be longer than 1000 characters.'),
        ], widget=TextArea())


class MessageDeleteForm(FlaskForm):
    pass
