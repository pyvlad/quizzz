from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField, BooleanField, SelectField, RadioField, FormField, FieldList
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, Optional


class TournamentForm(FlaskForm):
    tournament_name = StringField("Tournament Name", validators=[
                DataRequired(message="Tournament name cannot not be empty."),
                Length(max=100, message='Tournament name cannot be longer than 100 characters.'),
            ])
    has_started = BooleanField("Launch tournament?")
    has_finished = BooleanField("Finish tournament?")


class DeleteTournamentForm(FlaskForm):
    pass


class RoundForm(FlaskForm):
    quiz_id = SelectField("Select Quiz", coerce=int)
    start_time = DateField("Start Time", validators=(Optional(),))
    finish_time = DateField("Finish Time", validators=(Optional(),))


class DeleteRoundForm(FlaskForm):
    pass



class QuestionForm(Form):
    answer = RadioField()   # choices are added dynamically in views


def make_play_round_form(questions_per_quiz):
    class PlayRoundForm(FlaskForm):
        questions = FieldList(
            FormField(QuestionForm),
            min_entries=questions_per_quiz
        )
    return PlayRoundForm
