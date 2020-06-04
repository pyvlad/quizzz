"""
In this app, I have a bunch of resources that have <group_id> as part of URL.
I don't want to handle <group_id> in every single function.
What do I want instead?
1. Every time there is <group_id> in URL:
    a. it is popped from view args;
    b. it is added as g.group_id.
2. When <url_for> is used, all endpoints that expect <group_id>
    should receive it automatically from g.group_id.
"""
from flask import g


def init_app(app):
    @app.url_value_preprocessor
    def pull_group(endpoint, values):
        """
        Executed right after the request was matched based on the URL values.
        """
        # on 404 urls "values" is None
        if not values or "group_id" not in values:
            return

        g.group_id = values.pop('group_id')


    @app.url_defaults
    def add_group_id(endpoint, values):
        """
        In calls to url_for() automatically inject <group_id> value from g.group:
            a. if g.group is present;
            b. if the endpoint called by url_for() expects <group_id>,
                i.e. don't include it for home page or logout links.
            c. if <group_id> is not yet in dict of URL values provided in url_for() call.
        """
        if not "group_id" in g or 'group_id' in values:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'group_id'):
            values['group_id'] = g.group_id


    return app
