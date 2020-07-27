from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField, BooleanField, SelectField, RadioField, FormField, FieldList, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, InputRequired, Length, Optional, NumberRange

from quizzz.forms import ValidatedTextInput


class TournamentForm(FlaskForm):
    tournament_name = StringField("Tournament Name", validators=[
                DataRequired(message="Tournament name cannot not be empty."),
                Length(max=100, message='Tournament name cannot be longer than 100 characters.'),
            ], widget=ValidatedTextInput())
    is_active = BooleanField("Show tournament as active?")


class RoundForm(FlaskForm):
    quiz_id = SelectField("Select Quiz", coerce=int)
    start_date = DateField("Start Date")
    start_time_hours = IntegerField("Start Hours",
        validators=[ InputRequired(), NumberRange(min=0, max=23) ],
        widget=NumberInput(min=0, max=23)
    )
    start_time_minutes = IntegerField("Start Minutes",
        validators=[ InputRequired(), NumberRange(min=0, max=59) ],
        widget=NumberInput(min=0, max=59)
    )
    finish_date = DateField("Finish Date")
    finish_time_hours = IntegerField("Finish Hours",
        validators=[ InputRequired(), NumberRange(min=0, max=23) ],
        widget=NumberInput(min=0, max=23)
    )
    finish_time_minutes = IntegerField("Finish Minutes",
        validators=[ InputRequired(), NumberRange(min=0, max=59) ],
        widget=NumberInput(min=0, max=59)
    )


class QuestionForm(Form):
    answer = RadioField()   # choices are added dynamically in views


def make_play_round_form(questions_per_quiz):
    class PlayRoundForm(FlaskForm):
        questions = FieldList(
            FormField(QuestionForm),
            min_entries=questions_per_quiz
        )
    return PlayRoundForm
