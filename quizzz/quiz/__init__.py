from flask import Blueprint


bp = Blueprint('quiz', __name__, url_prefix='/groups/<int:group_id>/quiz')


from . import models
from . import views
