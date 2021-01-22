from werkzeug.local import LocalProxy
from flask import g, redirect, url_for, request

from flask_admin import Admin, BaseView, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm

from quizzz.db import get_db_session



# Common

# a. proxy to sqlalchemy session object
# https://werkzeug.palletsprojects.com/en/1.0.x/local/
db_session = LocalProxy(get_db_session)

# b. mixin to limit admin access to superuser only
class PrivateView:
    form_base_class = SecureForm

    def is_accessible(self):
        return g.user and g.user.is_superuser

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

# c. base class for model views requiring authorization
class PrivateModelView(PrivateView, ModelView):
    pass

# d. special index view requiring authorization
class IndexView(PrivateView, AdminIndexView):
    pass


# Set up Flask-Admin extension (needs IndexView - that's why not at the top)
URL_PREFIX = "/admin"
admin = Admin(
    name='Admin', 
    url=URL_PREFIX,
    template_mode='bootstrap3',
    index_view=IndexView(url=URL_PREFIX)
)


# Register views
from . import users