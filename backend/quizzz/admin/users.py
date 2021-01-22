import warnings

from sqlalchemy import func

from quizzz.auth.models import User
from quizzz.groups.models import Member
from quizzz.chat.models import Message
from quizzz.quizzes.models import Quiz
from quizzz.tournaments.models import Play
from quizzz.auth.forms import PasswordMixin

from . import admin, db_session, PrivateModelView


# a. List and manage user objects
class UserView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]
    column_exclude_list = ['uuid', 'password_hash',]
    column_searchable_list = ['name', 'email',]
    column_filters = ['can_create_groups', 'is_superuser','is_disabled','is_confirmed',]

    # create/edit views
    form_extra_fields = {
        "password": PasswordMixin.password,
        "password2": PasswordMixin.password2
    }

    form_create_rules = [
        "name", "email",
        "password", "password2",
        "is_confirmed", "can_create_groups", "is_disabled"
    ]

    form_edit_rules = [
        "name", "email",
        "is_confirmed", "can_create_groups", "is_disabled"
    ]

    form_excluded_columns = [
        "messages", 'quizzes', "plays", "tokens",   # don't load related collections
        "memberships",                              # many-to-many relation to groups - very inefficient
        "is_superuser",                             # available for change through CLI only
        "uuid", "password_hash", "time_created", "time_updated", # created automatically
    ]

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.create_uuid()
            model.set_password_hash(form.password.data)

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(UserView(User, db_session, 
        name="Users", category="Users", endpoint="users"))



# b. Ordered counts for related objects
admin.add_sub_category(name="User Metrics", parent_name="Users")


class UserCountView(PrivateModelView):
    can_view_details = True
    can_create = False
    can_edit = False
    can_delete = False

    # list view
    column_display_pk = True
    column_default_sort = [('id', True),]
    column_searchable_list = ['name', 'email',]

    _column_base_list = ('id', 'name', 'email',)    # extend in subclasses
    _object_base_list = (User.id, User.name, User.email,)


# b1. group counts
class UserGroupCountView(UserCountView):
    column_list = list(UserCountView._column_base_list) + ["groups"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Member.id).label('groups'))\
            .outerjoin(Member, Member.user_id == User.id)\
            .group_by(User.id)\
            .order_by(func.count(Member.id).desc())

admin.add_view(UserGroupCountView(User, db_session, 
    name="Groups", category="User Metrics", endpoint="user_group_counts"))


# b2. message counts
class UserMessageCountView(UserCountView):
    column_list = list(UserCountView._column_base_list) + ["messages"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Message.id).label('messages'))\
            .outerjoin(Message, Message.user_id == User.id)\
            .group_by(User.id)\
            .order_by(func.count(Message.id).desc())

admin.add_view(UserMessageCountView(User, db_session, 
    name="Messages", category="User Metrics", endpoint="user_message_counts"))


# b3. quiz counts
class UserQuizCountView(UserCountView):
    column_list = list(UserCountView._column_base_list) + ["quizzes"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Quiz.id).label('quizzes'))\
            .outerjoin(Quiz, Quiz.author_id == User.id)\
            .group_by(User.id)\
            .order_by(func.count(Quiz.id).desc())

admin.add_view(UserQuizCountView(User, db_session, 
    name="Quizzes", category="User Metrics", endpoint="user_quiz_counts"))


# b4. play counts
class UserPlayCountView(UserCountView):
    column_list = list(UserCountView._column_base_list) + ["plays"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Play.id).label('plays'))\
            .outerjoin(Play, Play.user_id == User.id)\
            .group_by(User.id)\
            .order_by(func.count(Play.id).desc())

admin.add_view(UserPlayCountView(User, db_session, 
    name="Plays", category="User Metrics", endpoint="user_play_counts"))