from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import (StringField, BooleanField, SelectField, RadioField, FormField, FieldList,
    IntegerField, HiddenField, DateTimeField)
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.widgets.html5 import NumberInput
from wtforms.validators import DataRequired, InputRequired, Length, Optional, NumberRange

from quizzz.forms import ValidatedTextInput
from .models import PlayAnswer



class TournamentForm(FlaskForm):
    tournament_name = StringField("Tournament Name", validators=[
                DataRequired(message="Tournament name cannot not be empty."),
                Length(max=100, message='Tournament name cannot be longer than 100 characters.'),
            ], widget=ValidatedTextInput())
    is_active = BooleanField("Show tournament as active?")

    def populate_object(self, obj, group_obj):
        obj.group = group_obj
        obj.name = self.tournament_name.data
        obj.is_active = bool(self.is_active.data)
        return obj


class RoundForm(FlaskForm):
    quiz_id = SelectField("Select Quiz", coerce=int)
    start_time = DateTimeField("Start Time",
        validators=[ InputRequired() ],
        format='%Y-%m-%dT%H:%M:%SZ')
    finish_time = DateTimeField("Finish Time",
        validators=[ InputRequired() ],
        format='%Y-%m-%dT%H:%M:%SZ')

    def populate_object(self, obj, tournament_id):
        obj.tournament_id = tournament_id
        obj.quiz_id = self.quiz_id.data
        obj.start_time = self.start_time.data
        obj.finish_time = self.finish_time.data
        # maybe process time, something like this:
        # obj.start_time = datetime.datetime.combine(self.start_date.data, datetime.datetime.min.time()) \
        #     + datetime.timedelta(hours=self.start_time_hours.data) \
        #     + datetime.timedelta(minutes=self.start_time_minutes.data)
        return self



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
        def populate_object(self, obj):
            # note: pre-load related round, quiz, questiions, question options object
            quiz = obj.round.quiz

            available_answers = {
                str(question.id): { str(option.id): option for option in question.options}
                for question in quiz.questions
            }

            answers = []
            for q in self.questions:
                # submitted question_id and option_id:
                question_id = q.form.question_id.data       # string
                option_id = q.form.answer.data              # string

                options = available_answers.get(question_id)
                if options is None:
                    raise QuestionIdMismatch()

                selected_option = options.get(option_id, None)
                answers += [PlayAnswer(play=obj, question_id=int(question_id), option=selected_option)]

            obj.answers = answers
            obj.is_submitted = True
            obj.result = len([answer for answer in answers if (answer.option and answer.option.is_correct)])

            return obj

    return PlayRoundForm



class QuestionIdMismatch(ValueError):
    pass