import os

from flask import Flask, render_template, g, redirect, url_for
from dotenv import load_dotenv
from flask_mail import Mail
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
    app.config["DATABASE_URI"] = 'sqlite:///' + os.path.join(app.instance_path, 'db.sqlite')
    
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

    # CLI commands and scripts
    from .db_dev import init_dev_db_command
    app.cli.add_command(init_dev_db_command)

    from .commands import promote_user
    app.cli.add_command(promote_user)

    from .migrations import db_cmd
    app.cli.add_command(db_cmd)

    return app
