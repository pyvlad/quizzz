from flask import Blueprint


bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder="templates")


from . import models
from . import views
