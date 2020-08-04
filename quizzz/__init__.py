import os

from flask import Flask, render_template, g, redirect, url_for
from flask_mail import Mail

mail = Mail()


def create_app(test_config=None):
    # create app
    app = Flask(__name__, instance_relative_config=True)

    # configure app
    app.config.from_mapping(
        SECRET_KEY='dev',
        WTF_CSRF_SECRET_KEY="dev",
        SESSION_COOKIE_SAMESITE="Lax",
        DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'db.sqlite'), # /// for absolute paths
        QUESTIONS_PER_QUIZ=2,
        OPTIONS_PER_QUESTION=4,
        SQLALCHEMY_ECHO=True,
        CHAT_MESSAGES_PER_PAGE=2,
        MAIL_SERVER = os.environ.get('MAIL_SERVER'),
        MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25),
        MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None,
        MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None,
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or os.environ.get("MAIL_USERNAME"),
        PASSWORD_RESET_TOKEN_VALIDITY=600
    )
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
    from .momentjs import momentjs
    app.jinja_env.globals['momentjs'] = momentjs

    # register blueprints
    from . import home
    app.register_blueprint(home.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import groups
    app.register_blueprint(groups.bp)

    from . import url_processors
    url_processors.init_app(app)

    from . import chat
    app.register_blueprint(chat.bp)

    from . import quizzes
    app.register_blueprint(quizzes.bp)

    from . import tournaments
    app.register_blueprint(tournaments.bp)

    from . import group
    app.register_blueprint(group.bp)

    app.add_url_rule('/', endpoint='index')

    return app
