import functools

from flask import g, abort


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(401, "You are not logged in.")

        return view(**kwargs)

    return wrapped_view
