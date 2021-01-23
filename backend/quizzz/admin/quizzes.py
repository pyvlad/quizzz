from sqlalchemy import func

from quizzz.auth.models import User
from quizzz.groups.models import Group
from quizzz.quizzes.models import Quiz, Question, Option
from quizzz.tournaments.models import Play

from . import admin, db_session, PrivateModelView


class QuizView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    can_create = False
    form_columns = ["topic", "num_questions", "num_options", "is_finalized", "questions", "round"]
    form_ajax_refs = {
        'round': {
            'fields': ('id',),
            'placeholder': 'Please enter round ID',
            'page_size': 10,
        },
        'questions': {
            'fields': ('text',),
            'placeholder': 'Please select',
            'page_size': 10,
        }
    }

admin.add_view(QuizView(Quiz, db_session, 
    name="Quizzes", category="Quizzes", endpoint="admin_quizzes"))



class QuestionView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    can_create = False
    form_columns = ["text", "comment", "options"]
    form_ajax_refs = {
        'options': {
            'fields': ('text',),
            'placeholder': 'Please enter',
            'page_size': 10,
        }
    }

admin.add_view(QuestionView(Question, db_session, 
    name="Questions", category="Quizzes", endpoint="admin_quiz_questions"))



class OptionView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    can_create = False
    form_columns = ["text", "is_correct"]

admin.add_view(OptionView(Option, db_session, 
    name="Options", category="Quizzes", endpoint="admin_question_options"))