from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from quizzz.forms import ValidatedTextInput

from .models import Group


class JoinGroupForm(FlaskForm):
    group_name = StringField('Group Name', 
        validators=[DataRequired(message="No group name submitted.")], 
        widget=ValidatedTextInput())
    password = StringField("Password")


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[
            DataRequired(),
            Length(min=2, message='Group name cannot be shorter than 2 letters.'),
            Length(max=20, message='Group name cannot be longer than 20 letters.'),
            Regexp(r"^[a-zA-Z][a-zA-Z0-9_\\.\- ]{1,19}$"),
        ], widget=ValidatedTextInput())
    password = StringField('Password', validators=[
            Length(max=10, message='Password cannot be longer than 20 letters.'),
            Regexp(r"[a-zA-Z0-9_\\.\-]{0,20}$"),
        ], widget=ValidatedTextInput())
    confirmation_needed = BooleanField("Require approval of new members from group admins?")

    def validate_name(self, field):
        group_name = field.data
        group = g.db.query(Group).filter(Group.name == group_name).first()
        if group:
            raise ValidationError(f'Group {group_name} already exists. Choose another name.')

    def populate_object(self, obj):
        obj.name = self.name.data
        obj.password = self.password.data
        obj.confirmation_needed = bool(self.confirmation_needed.data)
        return obj


class MemberForm(FlaskForm):
    is_approved = BooleanField("Accept this user as group member?")