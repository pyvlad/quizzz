from flask import Blueprint


bp = Blueprint('plays', __name__, url_prefix='/plays', template_folder="templates")


from . import models
from . import views
