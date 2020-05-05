import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create app
    app = Flask(__name__, instance_relative_config=True)

    # configure app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'db.sqlite'), # /// for absolute paths
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

    # register authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # an index page
    @app.route('/')
    def index():
        return render_template("index.html")

    return app
