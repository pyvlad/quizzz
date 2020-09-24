from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField, RadioField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import TextArea, TextInput
# from quizzz.forms import ValidatedTextInput, ValidatedTextArea



def make_option_form(finalize):
    validators = [Length(max=200, message='Option text cannot be longer than 200 characters.')]
    if finalize:
        validators += [
            DataRequired(message="Option text cannot be empty."),
        ]

    class OptionForm(Form):
        text = StringField(
            validators=validators,
            widget=TextInput()
        )

    return OptionForm



def make_question_form(options_per_question, finalize):
    OptionForm = make_option_form(finalize)

    text_validators = [
        Length(max=1000, message='Question text cannot be longer than 1000 characters.'),
    ]
    answer_validators = [ Optional() ]

    if finalize:
        text_validators += [
            DataRequired(message="Question text cannot be empty."),
        ]
        answer_validators = []

    class QuestionForm(Form):
        text = StringField(
            "Question Text",
            validators=text_validators,
            widget=TextArea()
        )
        options = FieldList(
            FormField(OptionForm),
            min_entries=options_per_question,
            max_entries=options_per_question,
        )
        answer = RadioField(
            validators=answer_validators,
            choices=[(str(i),"") for i in range(options_per_question)]
        )

    return QuestionForm



def make_quiz_form(questions_per_quiz, options_per_question, finalize=True):
    QuestionForm = make_question_form(options_per_question, finalize)

    class QuizForm(FlaskForm):
        topic = StringField(
            'Quiz Topic',
            validators=[
                DataRequired(message="Quiz topic must not be empty."),
                Length(max=100, message='Quiz topic cannot be longer than 100 characters.'),
            ],
            widget=TextInput()
        )
        questions = FieldList(
            FormField(QuestionForm),
            min_entries=questions_per_quiz,
            max_entries=questions_per_quiz,
        )

    return QuizForm
