from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class InvitationCodeForm(FlaskForm):
    invitation_code = StringField("Invitation Code", validators=[
            DataRequired(message="No Invitation Code submitted.")
        ])
