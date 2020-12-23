from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, EqualTo, Email

from quizzz.forms import ValidatedTextInput, ValidatedPasswordInput

from .models import User


class PasswordMixin:
    password = PasswordField('Password', validators=[
            DataRequired(),
            Length(min=6, message='Password cannot be shorter than 6 letters.'),
            Length(max=50, message='Password cannot be longer than 50 letters.'),
            EqualTo('password2', message='Passwords must match.'),
        ], widget=ValidatedPasswordInput())
    password2 = PasswordField('Repeat password', validators=[
            DataRequired()
        ])


class RegistrationForm(PasswordMixin, FlaskForm):
    username = StringField('Username', validators=[
            DataRequired(),
            Length(min=2, message='Username cannot be shorter than 2 letters.'),
            Length(max=20, message='Username cannot be longer than 20 letters.'),
            Regexp(r"^[a-zA-Z][a-zA-Z0-9_\\.]{1,19}$"),
        ], widget=ValidatedTextInput())

    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_username(self, field):
        username = field.data.lower()
        user = g.db.query(User).filter(User.name == username).first()
        if user:
            raise ValidationError(f'User {username} already exists.')

    def validate_email(self, field):
        email = field.data.lower()
        user = g.db.query(User).filter(User.email == email).first()
        if user:
            raise ValidationError(f'A user with email {email} is already registered.')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username is required.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])



class RequestResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])


class ResetPasswordForm(PasswordMixin, FlaskForm):
    submit = SubmitField('Request Password Reset')
