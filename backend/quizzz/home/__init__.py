from flask import Blueprint, g


bp = Blueprint('home', __name__)


from . import views
