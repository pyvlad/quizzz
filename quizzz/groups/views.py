from flask import g, flash, request, redirect, url_for, abort, render_template
from . import bp
from .models import Group, Member
from quizzz.db import get_db_session


@bp.route('/')
def show_all():
    return render_template('groups/all.html')


@bp.route('/<int:group_id>/')
def show_single(group_id):
    db = get_db_session()

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        abort(404, "group doesn't exist")

    return render_template('groups/single.html', group=group)


@bp.route('/join_group/')
def join():
    db = get_db_session()

    invitation_code = request.args.get("invitation_code")
    group = db.query(Group).filter(Group.invitation_code == invitation_code).first()
    if group:
        member = Member(group=group, user=g.user)
        db.add(member)
        db.commit()
        flash("Joined!")
    else:
        flash("Invalid invitation code!")

    return redirect(url_for('index'))
