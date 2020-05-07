from flask import Blueprint


bp = Blueprint('chat', __name__, url_prefix='/chat', template_folder="templates")


from . import models
from . import views
