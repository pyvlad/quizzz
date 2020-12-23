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
        if not g.group_membership or not g.group_membership:
            abort(403, "You're not a member of this group.")

    if level >= USER.IS_GROUP_ADMIN:
        if not g.group_membership or not g.group_membership.is_admin:
            abort(403, "You're not an admin of this group.")
