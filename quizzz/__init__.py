import os

from flask import Flask, render_template, g, redirect, url_for


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
