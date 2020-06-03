from flask import Blueprint


bp = Blueprint('tournaments', __name__, url_prefix='/groups/<int:group_id>/tournaments')


from . import models
from . import views_tournaments
from . import views_rounds
