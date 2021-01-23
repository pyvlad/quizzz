import warnings

from sqlalchemy import func

from quizzz.quizzes.models import Quiz
from quizzz.tournaments.models import Tournament, Round, Play, PlayAnswer

from . import admin, db_session, PrivateModelView



class TournamentView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    form_create_rules = ["group", "name", "is_active"]
    form_edit_rules = ["group", "name", "is_active", "rounds"]
    form_excluded_columns = ["time_created"]
    form_ajax_refs = {
        'group': {
            'fields': ('name', 'id',),
            'placeholder': 'Please select',
            'page_size': 10,
        },
        'rounds': {
            'fields': ('id',),
            'placeholder': 'Please select',
            'page_size': 10,
        }
    }

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(TournamentView(Tournament, db_session,  
        name="Tournaments", category="Tournaments", endpoint="admin_tournaments"))



class RoundView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    form_create_rules = ["tournament", "quiz", "start_time", "finish_time"]
    form_edit_rules = ["tournament", "quiz", "start_time", "finish_time", "plays", "messages"]
    form_ajax_refs = {
        'tournament': {
            'fields': ('name', 'id',),
            'placeholder': 'Please select',
            'page_size': 10,
        },
        'quiz': {
            'fields': ('topic', 'id',),
            'placeholder': 'Please select',
            'page_size': 10,
        },
        'plays': {
            'fields': ('id','user_id'),
            'placeholder': 'Please select',
            'page_size': 10,
        },
        'messages': {
            'fields': ('text', 'id',),
            'placeholder': 'Please select',
            'page_size': 10,
        }
    }

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(RoundView(Round, db_session,  
        name="Rounds", category="Tournaments", endpoint="admin_rounds"))



class PlayView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    can_create = False
    can_edit = False

admin.add_view(PlayView(Play, db_session,  
    name="Plays", category="Tournaments", endpoint="admin_plays"))



class AnswerView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]

    # create/edit views
    can_create = False
    can_edit = False

admin.add_view(AnswerView(PlayAnswer, db_session,  
    name="Answers", category="Tournaments", endpoint="admin_answers"))