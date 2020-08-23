from sqlalchemy.orm import selectinload
from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.auth import login_required
from quizzz.auth.models import User
from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm
from quizzz.permissions import USER, check_user_permissions

from . import bp
from .models import Group, Member
from .forms import InvitationCodeForm



@bp.route('/')
@login_required
def show_user_groups():
    user_groups = g.db.query(Member, Group)\
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

    form = InvitationCodeForm()
    leave_form = EmptyForm()

    return render_template('groups/user_groups.html', form=form, leave_form=leave_form, data=data)

# TODOS:
# 1. add 'leave' button
# 2. add 'remove' button with 'with_results'/"without results"
# 3. add 'ban' button - "remove" and add to list of "banned users"

@bp.route('/join_group/', methods=("POST",))
@login_required
def join():
    form = InvitationCodeForm()

    if form.validate():
        invitation_code = form.invitation_code.data

        group = g.db.query(Group).filter(Group.invitation_code == invitation_code).first()
        if not group:
            flash("Invalid invitation code!", Flashing.ERROR)
        else:
            user_group_ids = { m.group_id for m in g.user.memberships }
            if group.id not in user_group_ids:
                member = Member(group=group, user=g.user)
                g.db.add(member)
                g.db.commit()
                flash("Joined!", Flashing.SUCCESS)
            else:
                flash("You are already a member of this group!", Flashing.ERROR)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('groups.show_user_groups'))



@bp.route('/<int:group_id>/leave', methods=('POST',))
@login_required
def leave():
    form = EmptyForm()
    group_id = g.group_id   # see url_preprocessors for whole app

    if form.validate():
        result = g.db.query(Group, Member)\
            .join(Member, Group.id == Member.group_id)\
            .filter(Member.user_id == g.user.id)\
            .filter(Group.id == group_id)\
            .first()

        if result is None:
            abort(403, "You are not a member of this group.")

        group, membership = result
        if membership is None:
            abort(403, "You are not a member of this group.")

        if membership.is_admin:
            abort(403, "You are an admin, you cannot leave!")

        g.db.delete(membership) # TODO: mark as deleted instead
        g.db.commit()
        flash("You have left that group.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('groups.show_user_groups'))



@bp.route('/<int:group_id>/edit_member/<int:user_id>', methods=('GET', 'POST'))
@login_required
def remove_member(user_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    group_id = g.group_id   # see url_preprocessors for whole app

    result = g.db.query(User, Member)\
        .join(Member, User.id == Member.user_id)\
        .filter(User.id == user_id)\
        .filter(Member.group_id == group_id)\
        .first()

    if result is None:
        abort(400, "No such user.")

    user, membership = result
    if not membership:
        abort(400, "User is not a member of this group.")
    if membership.is_admin:
        abort(403, "You cannot remove an admin!")

    form = EmptyForm()
    if request.method == 'POST':
        if form.validate():
            g.db.delete(membership)
            g.db.commit()
            flash("User %s has been removed." % user.name, Flashing.SUCCESS)
            return redirect(url_for('group.show_members'))
        else:
            flash("Invalid form submitted.", Flashing.ERROR)

    data = {
        "username": user.name
    }

    return render_template('groups/remove_member.html', form=form, data=data)
