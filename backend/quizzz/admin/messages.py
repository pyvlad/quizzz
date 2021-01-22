from sqlalchemy import func

from quizzz.auth.models import User
from quizzz.chat.models import Message
from quizzz.tournaments.models import Play

from . import admin, db_session, PrivateModelView


class MessageView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_list = ['id', "user", "group", "round_id", "text", "time_created", "time_updated"]
    column_default_sort = [('id', True),]
    column_searchable_list = ["text"]
    column_filters = ['user', 'group', 'round_id']

    # create/edit views
    form_columns = ["text", "round_id", "user", "group"]
    form_ajax_refs = {
        'user': {
            'fields': ('name', 'email'),        # fields to search in with 'LIKE' as you type 
            'placeholder': 'Please select',
            'page_size': 10,
            'minimum_input_length': 0,          # send as cursor is entered into the field
        },
        'group': {
            'fields': ('name',),
            'placeholder': 'Please select',
            'page_size': 10,
            'minimum_input_length': 0,
        }
    }

admin.add_view(MessageView(Message, db_session, 
    name="Messages", endpoint="admin_messages"))