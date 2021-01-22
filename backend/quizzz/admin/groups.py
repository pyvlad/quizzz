from sqlalchemy import func

from quizzz.auth.models import User
from quizzz.groups.models import Group, Member
from quizzz.chat.models import Message
from quizzz.quizzes.models import Quiz
from quizzz.tournaments.models import Play, Tournament
from quizzz.auth.forms import PasswordMixin

from . import admin, db_session, PrivateModelView



# a. List and manage group objects
class GroupView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]
    column_searchable_list = ['name',]
    column_filters = ['id',]

    # create/edit views
    form_excluded_columns = [
        "members", "messages", "quizzes", "tournaments",    # don't load related collections
        "time_created", "time_updated",                     # created automatically
    ]

admin.add_view(GroupView(Group, db_session, 
    name="Groups", category="Groups", endpoint="admin_groups"))



# b. List and manage member objects
class MemberView(PrivateModelView):
    column_display_pk = True
    can_view_details = True

    # list view
    column_default_sort = [('id', True),]
    column_filters = ['is_admin',]

    # create/edit views
    form_excluded_columns = [
        "time_created", "time_updated",                     # created automatically
    ]

admin.add_view(MemberView(Member, db_session, 
    name="Members", category="Groups", endpoint="group_members"))



# c. Ordered counts for related objects
admin.add_sub_category(name="Group Metrics", parent_name="Groups")


class GroupCountView(PrivateModelView):
    can_view_details = False
    can_create = False
    can_edit = False
    can_delete = False

    # list view
    column_display_pk = True
    column_default_sort = [('id', True),]
    column_searchable_list = ['name',]

    _column_base_list = ('id', 'name', 'time_created', 'time_updated')    # extend in subclasses
    _object_base_list = (Group.id, Group.name, Group.time_created, Group.time_updated)


# c1. Group Counts
class GroupUserCountView(GroupCountView):
    column_list = list(GroupCountView._column_base_list) + ["members"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Member.id).label('members'))\
            .outerjoin(Member, Member.group_id == Group.id)\
            .group_by(Group.id)\
            .order_by(func.count(Group.id).desc())

admin.add_view(GroupUserCountView(Group, db_session, 
    name="Members", category="Group Metrics", endpoint="group_member_counts"))


# c2. message counts
class GroupMessageCountView(GroupCountView):
    column_list = list(GroupCountView._column_base_list) + ["messages"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Message.id).label('messages'))\
            .outerjoin(Message, Message.group_id == Group.id)\
            .group_by(Group.id)\
            .order_by(func.count(Message.id).desc())

admin.add_view(GroupMessageCountView(Group, db_session, 
    name="Messages", category="Group Metrics", endpoint="group_message_counts"))


# c3. quiz counts
class GroupQuizCountView(GroupCountView):
    column_list = list(GroupCountView._column_base_list) + ["quizzes"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Quiz.id).label('quizzes'))\
            .outerjoin(Quiz, Quiz.group_id == Group.id)\
            .group_by(Group.id)\
            .order_by(func.count(Quiz.id).desc())

admin.add_view(GroupQuizCountView(Group, db_session, 
    name="Quizzes", category="Group Metrics", endpoint="group_quiz_counts"))


# c4. tournament counts
class GroupTournamentCountView(GroupCountView):
    column_list = list(GroupCountView._column_base_list) + ["tournaments"]
    
    def get_query(self):
        return db_session\
            .query(*self._object_base_list, func.count(Tournament.id).label('tournaments'))\
            .outerjoin(Tournament, Tournament.group_id == Group.id)\
            .group_by(Group.id)\
            .order_by(func.count(Tournament.id).desc())

admin.add_view(GroupTournamentCountView(Group, db_session, 
    name="Tournaments", category="Group Metrics", endpoint="group_tournament_counts"))