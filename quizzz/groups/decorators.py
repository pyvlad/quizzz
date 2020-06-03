import functools

from flask import request, g, abort

from quizzz.db import get_db_session

from .models import Member


def membership_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db_session()
        user_group_ids = set(gid for (gid,) in
            db.query(Member.group_id).filter(Member.user_id == g.user.id).all())
        if request.view_args["group_id"] not in user_group_ids:
            abort(403, "You're not a member of this group.")

        return view(**kwargs)

    return wrapped_view
