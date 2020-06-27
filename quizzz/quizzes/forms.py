from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField, RadioField, FieldList, FormField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

from quizzz.forms import ValidatedTextInput, ValidatedTextArea


class QuizDeleteForm(FlaskForm):
    pass


class OptionForm(Form):
    text = StringField(validators=[
                DataRequired(message="Option text cannot not be empty."),
                Length(max=200, message='Option text cannot be longer than 200 characters.'),
            ], widget=ValidatedTextInput())


def get_question_form(options_per_question):
    class QuestionForm(Form):
        text = StringField("Question Text", validators=[
                    DataRequired(message="Question text cannot not be empty."),
                    Length(max=1000, message='Question text cannot be longer than 1000 characters.'),
                ], widget=ValidatedTextArea())
        options = FieldList(
            FormField(OptionForm),
            min_entries=options_per_question
        )
        answer = RadioField(choices=[(str(i),"") for i in range(options_per_question)])
    return QuestionForm



def make_quiz_form(questions_per_quiz, options_per_question):
    class QuizForm(FlaskForm):
        topic = StringField('Quiz Topic', validators=[
                    DataRequired(message="Quiz topic must not be empty."),
                    Length(max=100, message='Quiz topic cannot be longer than 100 characters.'),
                ], widget=ValidatedTextInput())
        is_finalized = RadioField("Submit Quiz?", choices=[
                    ("0", "No, I am not finished yet and want to review/update it later."),
                    ("1", "Yes, the quiz is finished and checked and I want it added to the group's quiz pool."),
                ], validators=[DataRequired(message="Select whether you want to submit quiz.")])
        questions = FieldList(
            FormField(get_question_form(options_per_question)),
            min_entries=questions_per_quiz
        )

    return QuizForm
