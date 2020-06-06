from flask import Blueprint


bp = Blueprint('quizzes', __name__, url_prefix='/groups/<int:group_id>/quizzes')


from . import models
from . import views
