import traceback

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from flask import g, flash, request, redirect, url_for, abort, render_template, current_app

from quizzz.auth import login_required
from quizzz.auth.models import User
from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm
from quizzz.permissions import USER, check_user_permissions

from . import bp
from .models import Group, Member
from .forms import JoinGroupForm, GroupForm, MemberForm



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

    form = JoinGroupForm()
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

    group = None
    if g.group_id:
        group = g.group
    else:
        group = Group(max_members=current_app.config["MAX_MEMBERS_PER_GROUP"])

    membership = (Member(user=g.user, group=group, is_admin=True)
        if not g.group_membership else g.group_membership)

    if request.method == 'POST':
        form = GroupForm()
        form.populate_object(group)
        
        with g.db.no_autoflush:
            repeat_group = g.db.query(Group)\
                .filter(func.lower(Group.name) == (group.name or "").lower())\
                .first()
            if repeat_group and repeat_group.id != group.id:
                flash("Group name already in use. Choose another one.", Flashing.ERROR)
                return redirect(url_for('groups.edit', group_id=g.group_id))

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
            password=group.password,
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
    Join an existing group by its name and (optional) password.
    Creates a new basic membership.
    """
    form = JoinGroupForm()

    if form.validate():
        group_name = form.group_name.data

        group = g.db.query(Group).filter(Group.name == group_name).first()
        if not group:
            flash("Group does not exist!", Flashing.ERROR)
            return redirect(url_for('groups.index'))

        user_group_ids = { m.group_id for m in g.user.memberships }
        if group.id in user_group_ids:
            flash("You are already a member of this group!", Flashing.ERROR)
            return redirect(url_for('groups.index'))

        if group.password and (group.password != form.password.data):
            flash("Wrong password!", Flashing.ERROR)
            return redirect(url_for('groups.index'))

        if group.max_members is not None:     # None means 'unlimited'
            member_count = g.db.query(Member).filter(Member.group_id == group.id).count()
            if member_count >= group.max_members:
                flash("Cannot join. Too many members: %s." % group.max_members, Flashing.ERROR)
                return redirect(url_for('groups.index'))

        member = Member(group=group, user=g.user, is_approved=(not group.confirmation_needed))
        g.db.add(member)
        g.db.commit()
        flash("Joined!", Flashing.SUCCESS)

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
                "is_approved": m.is_approved,
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

    if request.method == 'POST':
        form = MemberForm()
        membership.is_approved = form.is_approved.data

        g.db.add(membership)
        g.db.commit()

        flash("User %s has been %s." % (user.name, 
            "approved" if form.is_approved.data else "disabled"), Flashing.SUCCESS)
        return redirect(url_for('groups.list_members'))
    else:
        form = MemberForm(is_approved=membership.is_approved)

    data = {
        "user": {
            "name": user.name,
            "id": user.id,
        }
    }

    delete_form = EmptyForm()

    navbar_items = [
      ("Groups", url_for("groups.index"), False),
      (g.group.name, url_for("group.show_group_page"), True),
      ("Members", url_for("groups.list_members"), False),
      (data["user"]["name"], "", True)
    ]

    return render_template('groups/edit_member.html', form=form, delete_form=delete_form, 
        data=data, navbar_items=navbar_items)



@bp.route('/<int:group_id>/members/<int:user_id>/delete', methods=('POST',))
def delete_member(user_id):
    """
    Delete member from group.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    form = EmptyForm()

    if form.validate():
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
        if membership.is_admin:
            abort(403, "Group admin cannot be deleted.")

        g.db.delete(membership)
        g.db.commit()
        
        flash("User %s has been removed from group <%s>." % (user.name, g.group.name), Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('groups.list_members'))