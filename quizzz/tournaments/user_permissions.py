from flask import g, abort


class USER:
    IS_LOGGED_IN = 1
    IS_GROUP_MEMBER = 2
    IS_GROUP_ADMIN = 3



def check_user_permissions(level):
    if level >= USER.IS_LOGGED_IN:
        if not g.user:
            abort(403, "You're not logged in.")

    if level >= USER.IS_GROUP_MEMBER:
        user_group_ids = { m.group_id for m in g.user.memberships }
        if g.group.id not in user_group_ids:
            abort(403, "You're not a member of this group.")

    if level >= USER.IS_GROUP_ADMIN:
        group_memberships = list(g.group.members)
        group_member_user_ids = [m.user_id for m in group_memberships]
        membership = group_memberships[group_member_user_ids.index(g.user.id)]
        if not membership.is_admin:
            abort(403, "You're not an admin of this group.")
