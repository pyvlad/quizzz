from flask import Blueprint, session, g

from quizzz.db import get_db_session


bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder="templates")


from . import models
from .decorators import login_required
from . import views


@bp.before_app_request
def load_logged_in_user():
    """
    Load user from DB if 'user_id' is in session.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db_session()
        g.user = db.query(models.User).filter(models.User.id == user_id).one()
