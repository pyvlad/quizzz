import os

from flask import Flask, render_template, g, redirect, url_for
from dotenv import load_dotenv
from flask_mail import Mail
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from .momentjs import MomentJS

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

mail = Mail()
momentjs = MomentJS()


def create_app(test_config=None):
    # create app
    app = Flask(__name__, instance_relative_config=True)

    # apply default settings
    from . import default_settings
    app.config.from_object(default_settings)
    # set up database uri separately (no access to instance_path in default_settings)
    # below, /// is for an absolute path
    app.config["DATABASE_URI"] = os.environ.get("DATABASE_URI") or (
        'sqlite:///' + os.path.join(app.instance_path, 'db.sqlite'))
    
    # override default settings
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)    # instance config if it exists
    else:
        app.config.from_mapping(test_config)                # test config when passed

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize sentry
    DISABLE_SENTRY = os.environ.get("DISABLE_SENTRY")
    # "DISABLE_SENTRY" lets having one .env file for development and testing
    if not DISABLE_SENTRY:
        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )

    # initialize database functionality
    from . import db
    db.init_app(app)

    # initialize mail support
    mail.init_app(app)

    # initialize momentjs support
    momentjs.init_app(app)

    # register blueprints
    from . import home
    app.register_blueprint(home.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import groups
    app.register_blueprint(groups.bp)

    from . import group_url_processors
    group_url_processors.init_app(app)

    from . import chat
    app.register_blueprint(chat.bp)

    from . import quizzes
    app.register_blueprint(quizzes.bp)

    from . import tournaments
    app.register_blueprint(tournaments.bp)

    from . import group
    app.register_blueprint(group.bp)

    app.add_url_rule('/', endpoint='index')

    # admin interface
    from .admin import admin
    admin.init_app(app)

    # CLI commands and scripts
    from .db_dev_data import add_dev_data
    app.cli.add_command(add_dev_data)

    from .commands import promote_user, create_superuser
    app.cli.add_command(promote_user)
    app.cli.add_command(create_superuser)

    from .migrations import db_cmd
    app.cli.add_command(db_cmd)

    return app
