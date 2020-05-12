from flask import Blueprint


bp = Blueprint('quiz', __name__, url_prefix='/quiz', template_folder="templates")


from . import models
from . import views
