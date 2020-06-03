from flask import Blueprint


bp = Blueprint('groups', __name__, url_prefix='/groups', template_folder="templates")


from . import models
from .decorators import membership_required
from . import views
