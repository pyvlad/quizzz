from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError

from quizzz.db import get_db_session

from .models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
            DataRequired(message="Username is required."),
            Length(min=2, message='Username cannot be shorter than 2 letters.'),
            Length(max=20, message='Username cannot be longer than 20 letters.'),
        ])
    password = PasswordField('Password', validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message='Password cannot be shorter than 2 letters.'),
            Length(max=50, message='Password cannot be longer than 50 letters.'),
        ])

    def validate_username(self, field):
        db = get_db_session()
        username = field.data.lower()
        user = db.query(User).filter(User.name == username).first()
        if user:
            raise ValidationError(f'User {username} already exists.')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username is required.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
