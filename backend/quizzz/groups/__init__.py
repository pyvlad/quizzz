from flask import Blueprint


bp = Blueprint('groups', __name__, url_prefix='/groups')


from . import models
from . import views
