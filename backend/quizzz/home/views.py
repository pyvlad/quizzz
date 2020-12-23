from flask import render_template, g, url_for, redirect
from . import bp


@bp.route("/")
def index():
    if g.user:
        return redirect(url_for('groups.index'))

    return render_template("home/index.html")
