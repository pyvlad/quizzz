from sqlalchemy.orm import selectinload
from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.db import get_db_session
from quizzz.auth import login_required
from quizzz.flashing import Flashing

from . import bp
from .models import Group, Member



@bp.route('/')
@login_required
def show_user_groups():
    db = get_db_session()
    user_groups = db.query(Member, Group)\
        .filter(Member.user_id == g.user.id)\
        .filter(Member.group_id == Group.id)\
        .all()

    data = {
        "user_groups": [
            {
                "id": group.id,
                "name": group.name,
                "is_admin": m.is_admin
            } for m, group in user_groups
        ]
    }
    return render_template('groups/user_groups.html', data=data)



@bp.route('/<int:group_id>/')
def show_group_page():
    data = {
        "group": {
            "id": g.group.id,
            "name": g.group.name
        }
    }
    return render_template('groups/group_page.html', data=data)



@bp.route('/join_group/', methods=("POST",))
@login_required
def join():
    invitation_code = request.form["invitation_code"]

    db = get_db_session()
    group = db.query(Group).filter(Group.invitation_code == invitation_code).first()
    if not group:
        flash("Invalid invitation code!", Flashing.ERROR)
    else:
        user_group_ids = { m.group_id for m in g.user.memberships }
        if group.id not in user_group_ids:
            member = Member(group=group, user=g.user)
            db.add(member)
            db.commit()
            flash("Joined!", Flashing.SUCCESS)
        else:
            flash("You are already a member of this group!", Flashing.ERROR)

    return redirect(url_for('groups.show_user_groups'))
