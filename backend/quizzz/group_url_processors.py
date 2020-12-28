"""
In this app, I have a bunch of resources that have <group_id> as part of URL.
I don't want to handle <group_id> in every single function.
What do I want instead?
1. Every time there is <group_id> in URL:
    a. it is popped from view args;
    b. it is added as g.group_id.
    c. ORM objects are loaded and attached as g.group and g.group_membership for current user
2. When <url_for> is used, all endpoints that expect <group_id>
    should receive it automatically from g.group_id.

URL processors short intro:
https://flask.palletsprojects.com/en/1.1.x/patterns/urlprocessors/
In short:
- URL value preprocessors are executed right after the request was matched 
  (before the before_request() function);
- URL defaults let you automatically inject values into url_for() calls.
"""
from flask import g, request, abort
from quizzz.groups.models import Group, Member



def init_app(app):

    # note: functions are declared inside the init_app function to have access
    #       to the app instance (e.g. see add_group_id below)

    def pull_group(endpoint, values):
        """
        Function to be used as URL value preprocessor in the app.
        Pops <group_id> from the values dict if it's part of URL and attach to g. 
        """
        # on 404 urls "values" is None
        if not values:
            return
        # skip if <group_id> is not a part of the URL
        if "group_id" not in values:
            return
        g.group_id = values.pop('group_id')


    def add_group_id(endpoint, values):
        """
        Function to be used as URL default (for url_for) in the app.
        Automatically injects <group_id> value from g.group in calls to url_for().
        """
        # don't automatically inject anything if you are currently on a non-group page:
        if 'group_id' not in g:
            return
        # skip if <group_id> is already in the dict of URL values 
        # (explicitly provided in url_for() call):
        if 'group_id' in values:
            return
        # inject group_id if the endpoint called by url_for() expects <group_id>,
        # i.e. don't include it for home page or logout links:
        if app.url_map.is_endpoint_expecting(endpoint, 'group_id'):
            values['group_id'] = g.group_id


    def load_group_and_membership():
        """
        Load group and membership from DB if 'group_id' is in g.
        """
        # skip for static assets
        if request.path.startswith("/static/"):
            return

        if "group_id" in g:
            # TODO: currently <group_id> in URL requires login and group membership
            # do I want to keep it this way?
            if g.user is None:
                abort(401, "You are not logged in.")

            # group_id == 0 is used while creating new group:
            if g.group_id == 0:
                g.group, g.group_membership = (None, None)
            else:
                result = g.db.query(Group, Member)\
                    .join(Member, Group.id == Member.group_id)\
                    .filter(Member.user_id == g.user.id)\
                    .filter(Group.id == g.group_id)\
                    .first()
                if result is None:
                    abort(403, "You are not a member of this group.")
                else:
                    g.group, g.group_membership = result

        else:
            g.group, g.group_membership = (None, None)


    app.url_value_preprocessor(pull_group)
    app.before_request(load_group_and_membership)
    app.url_defaults(add_group_id)

    return app
