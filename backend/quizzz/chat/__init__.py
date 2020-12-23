from flask import Blueprint


bp = Blueprint('chat', __name__, url_prefix='/groups/<int:group_id>/chat')


from . import models
from . import views
