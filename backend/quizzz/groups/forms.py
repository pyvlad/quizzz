from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from quizzz.forms import ValidatedTextInput

from .models import Group


class InvitationCodeForm(FlaskForm):
    invitation_code = StringField("Invitation Code", validators=[
            DataRequired(message="No Invitation Code submitted.")
        ])


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[
            DataRequired(),
            Length(min=2, message='Group name cannot be shorter than 2 letters.'),
            Length(max=20, message='Group name cannot be longer than 20 letters.'),
            Regexp(r"^[a-zA-Z][a-zA-Z0-9_\\.\- ]{1,19}$"),
        ], widget=ValidatedTextInput())
    invitation_code = StringField('Invitation Code', validators=[
            DataRequired(),
            Length(min=2, message='Invitation code cannot be shorter than 2 letters.'),
            Length(max=10, message='Invitation code cannot be longer than 10 letters.'),
            Regexp(r"[a-zA-Z0-9_\\.\-]{2,10}$"),
        ], widget=ValidatedTextInput())
    confirmation_needed = BooleanField("Require approval of new members from group admins?")

    def validate_name(self, field):
        group_name = field.data
        group = g.db.query(Group).filter(Group.name == group_name).first()
        if group:
            raise ValidationError(f'Group {group_name} already exists. Choose another name.')

    def validate_invitation_code(self, field):
        invitation_code = field.data.lower()
        group = g.db.query(Group).filter(Group.invitation_code == invitation_code).first()
        if group:
            raise ValidationError(f'Invitation code {invitation_code} is used by another group.')
