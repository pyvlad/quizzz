from flask import Blueprint, request, g, abort

from quizzz.db import get_db_session
from quizzz.groups.models import Group, Member


bp = Blueprint('groups', __name__, url_prefix='/groups')


from . import models
from . import views


@bp.before_app_request
def load_group_and_membership():
    """
    Load group and membership from DB if 'group_id' is in g (see app url_preprocessors).
    """
    # TODO delete this in production
    if '/static/' in request.path:
        return

    if "group_id" in g:
        if g.user is None:
            abort(401, "You are not logged in.")

        db = get_db_session()
        result = db.query(Group, Member)\
            .join(Member, Group.id == Member.group_id)\
            .filter(Member.user_id == g.user.id)\
            .filter(Group.id == g.group_id)\
            .first()

        if result is None:
            abort(403, "You are not a member of this group.")
        else:
            g.group, g.group_membership = result

    else:
        g.group = None
        g.group_membership = None
