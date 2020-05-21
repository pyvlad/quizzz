from flask import Blueprint, g
from quizzz.db import get_db_session
from quizzz.groups.models import Group


bp = Blueprint('quiz', __name__, url_prefix='/groups/<int:group_id>/quiz', template_folder="templates")


@bp.url_defaults
def add_group_id(endpoint, values):
    if 'group_id' in values or not g.group:
        return
    values['group_id'] = g.group.id


@bp.url_value_preprocessor
def pull_group(endpoint, values):
    group_id = values.pop('group_id')

    db = get_db_session()
    group = db.query(Group).filter(Group.id == group_id).first()
    if group:
        g.group = group
    else:
        abort(400, "group doesn't exist")


from . import models
from . import views
