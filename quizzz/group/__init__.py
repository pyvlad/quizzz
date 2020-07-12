from flask import Blueprint


bp = Blueprint('group', __name__, url_prefix='/groups/<int:group_id>/')


from . import views
