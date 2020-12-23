from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import (StringField, BooleanField, SelectField, RadioField, FormField, FieldList,
    IntegerField, HiddenField, DateTimeField)
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
    start_time = DateTimeField("Start Time",
        validators=[ InputRequired() ],
        format='%Y-%m-%dT%H:%M:%SZ')
    finish_time = DateTimeField("Finish Time",
        validators=[ InputRequired() ],
        format='%Y-%m-%dT%H:%M:%SZ')


class QuestionForm(Form):
    question_id = HiddenField(
        validators=[ InputRequired() ]
    )
    answer = RadioField(
        validators=[ Optional() ]
    )   # choices are added dynamically in views


def make_play_round_form(questions_per_quiz):
    class PlayRoundForm(FlaskForm):
        questions = FieldList(
            FormField(QuestionForm),
            # create blank entries if provided input in formdata is not enough:
            min_entries=questions_per_quiz,
            # accept no more than this many entries as input, even if more exist in formdata:
            max_entries=questions_per_quiz
        )
    return PlayRoundForm
