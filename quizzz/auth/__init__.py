from flask import Blueprint, session, g, request


bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder="templates")


from . import models
from .decorators import login_required
from . import views


@bp.before_app_request
def load_logged_in_user():
    """
    Load user from DB if 'user_id' is in session.
    """
    # TODO delete this in production
    if '/static/' in request.path:
        return

    user_uuid = session.get('user_id')

    if user_uuid is None:
        g.user = None
    else:
        g.user = g.db.query(models.User).filter(models.User.uuid == user_uuid).one()
        if g.user.is_deleted:
            g.user = None
