from flask import g, flash, request, redirect, url_for, abort, render_template
from . import bp
from .models import Group, Member
from quizzz.db import get_db_session


@bp.route('/')
def show_all():
    if not g.user:
        abort(403, "You're not logged in.")
    return render_template('groups/all.html', user_memberships=g.user.memberships)


@bp.route('/<int:group_id>/')
def show_single(group_id):
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if group_id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    db = get_db_session()
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        abort(404, "This group doesn't exist.")

    return render_template('groups/single.html', group=group)


@bp.route('/join_group/')
def join():
    if not g.user:
        abort(403, "You're not logged in.")

    invitation_code = request.args.get("invitation_code")

    db = get_db_session()
    group = db.query(Group).filter(Group.invitation_code == invitation_code).first()
    if not group:
        flash("Invalid invitation code!")
    else:
        user_group_ids = [m.group_id for m in g.user.memberships]
        if group.id not in user_group_ids:
            member = Member(group=group, user=g.user)
            db.add(member)
            db.commit()
            flash("Joined!")
        else:
            flash("You're already a member of this group!")

    return redirect(url_for('index'))
