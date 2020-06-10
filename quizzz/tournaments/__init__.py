from flask import Blueprint


bp = Blueprint('tournaments', __name__, url_prefix='/groups/<int:group_id>/')


from . import models
from . import views
from . import admin_views
