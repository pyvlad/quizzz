import traceback

from sqlalchemy.orm import selectinload
from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.auth import login_required
from quizzz.auth.models import User
from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm
from quizzz.permissions import USER, check_user_permissions

from . import bp
from .models import Group, Member
from .forms import InvitationCodeForm, GroupForm



@bp.route('/')
@login_required
def index():
    """
    Index page for group management.
    Shows list of groups that a user is a member of.
    Provides a form to join new groups.
    """
    user_groups = g.db.query(Member, Group)\
        .filter(Member.user_id == g.user.id)\
        .filter(Member.group_id == Group.id)\
        .all()

    data = {
        "user_groups": [
            {
                "id": group.id,
                "name": group.name,
                "is_admin": m.is_admin,
                "view_url": url_for('group.show_group_page', group_id=group.id),
                "edit_url": url_for('groups.edit', group_id=group.id),
                "leave_url": url_for('groups.leave', group_id=group.id),
            } for m, group in user_groups
        ],
        "has_edit_permissions": g.user.can_create_groups,
    }

    form = InvitationCodeForm()
    leave_form = EmptyForm()

    navbar_items = [('Groups', "", False)]

    return render_template('groups/index.html', form=form, leave_form=leave_form,
        data=data, navbar_items=navbar_items)


# ----- CREATE/EDIT -----
@bp.route('/<int:group_id>/edit', methods=("GET", "POST"))
def edit():
    """
    Edit group.
    """
    if g.group_id == 0:
        if not g.user.can_create_groups:
            abort(403, "You cannot create groups.")
    else:
        check_user_permissions(USER.IS_GROUP_ADMIN)

    group = (Group() if not g.group_id else g.group)
    membership = (Member(user=g.user, group=group, is_admin=True)
        if not g.group_membership else g.group_membership)

    if request.method == 'POST':
        form = GroupForm()
        group.populate_from_wtform(form)

        try:
            g.db.add(group)
            g.db.add(membership)
            g.db.commit()
        except:
            traceback.print_exc()
            g.db.rollback()
            flash("Group could not be created!", Flashing.ERROR)
        else:
            flash("Group successfully created/updated.", Flashing.SUCCESS)
            return redirect(url_for('groups.index'))

    else:
        form = GroupForm(
            name=group.name,
            invitation_code=group.invitation_code,
            confirmation_needed=group.confirmation_needed,
        )

    data = {
        "group": {
            "id": group.id,
            "name": group.name
        }
    }

    delete_form = EmptyForm()

    navbar_items = [
      ("Groups", url_for("groups.index"), False),
      ((data["group"]["id"] and "Edit Group") or "New Group", "", False)
    ]

    return render_template('groups/edit.html', form=form, delete_form=delete_form,
        data=data, navbar_items=navbar_items)



@bp.route('/<int:group_id>/delete', methods=('POST',))
def delete():
    """
    Delete group.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    form = EmptyForm()

    if form.validate():
        g.db.delete(g.group)
        g.db.commit()
        flash("Group has been deleted.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('groups.index'))



# ----- MEMBERSHIP MANAGEMENT -----
# a. JOIN/LEAVE
@bp.route('/join', methods=("POST",))
@login_required
def join():
    """
    Join an existing group by a known invitation code.
    Creates a new basic membership.
    """
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

    return redirect(url_for('groups.index'))



@bp.route('/<int:group_id>/leave', methods=('POST',))
def leave():
    """
    Leave a group you are a member of.
    Deletes existing membership.
    """
    form = EmptyForm()

    if form.validate():
        # g.group and g.group_membership are handled in url_processors
        if g.group_membership.is_admin:
            abort(403, "You are an admin, you cannot leave!")

        g.db.delete(g.group_membership) # TODO: mark as deleted instead
        g.db.commit()
        flash("You have left that group.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('groups.index'))



# b. LIST MEMBERS
@bp.route('/<int:group_id>/members/')
def list_members():
    members = g.db.query(Member, User.name, User.time_created)\
        .join(User, Member.user_id == User.id)\
        .filter(Member.group_id == g.group.id)\
        .order_by(User.name.asc())\
        .all()

    data = {
        "members": [
            {
                "user_id": m.id,
                "name": username,
                "time_created": time_created,
                "is_admin": m.is_admin,
                "edit_url": url_for("groups.edit_member", user_id=m.user_id),
            } for m, username, time_created in members
        ],
        "is_admin": g.group_membership and g.group_membership.is_admin
    }

    navbar_items = [
      ("Groups", url_for("groups.index"), False),
      (g.group.name, url_for("group.show_group_page"), True),
      ("Members", "", False)
    ]

    return render_template('groups/members.html', data=data, navbar_items=navbar_items)



# c. EDIT MEMBER (FOR GROUP ADMINS)
@bp.route('/<int:group_id>/members/<int:user_id>/edit', methods=('GET', 'POST'))
def edit_member(user_id):
    """
    Modify user membership parameters:
    - delete user membership;
    - ban user from entering group (TODO);
    - delete user results (TODO);
    - give user admin rights (TODO);
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    result = g.db.query(User, Member)\
        .join(Member, User.id == Member.user_id)\
        .filter(User.id == user_id)\
        .filter(Member.group_id == g.group_id)\
        .first()

    if result is None:
        abort(400, "No such user.")
    user, membership = result
    if not membership:
        abort(400, "User is not a member of this group.")

    form = EmptyForm()
    if request.method == 'POST':
        if form.validate():
            if membership.is_admin:
                abort(403, "Group admin cannot be removed!")

            g.db.delete(membership)
            g.db.commit()
            flash("User %s has been removed." % user.name, Flashing.SUCCESS)
            return redirect(url_for('groups.list_members'))
        else:
            flash("Invalid form submitted.", Flashing.ERROR)

    data = {
        "username": user.name
    }

    navbar_items = [
      ("Groups", url_for("groups.index"), False),
      (g.group.name, url_for("group.show_group_page"), True),
      ("Members", url_for("groups.list_members"), False),
      (data["username"], "", True)
    ]

    return render_template('groups/edit_member.html', form=form, data=data, navbar_items=navbar_items)
