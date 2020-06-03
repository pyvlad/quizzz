from flask import Blueprint


bp = Blueprint('plays', __name__, url_prefix='/groups/<int:group_id>/plays')


from . import models
from . import views
