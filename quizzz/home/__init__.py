from flask import Blueprint, g
from quizzz.db import get_db_session


bp = Blueprint('home', __name__, template_folder="templates")


from . import views
