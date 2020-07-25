import click
from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.event import listen


Base = declarative_base()
Session = None


def get_db_session():
    """
    Create the request-local db session if not present, or return the existing one.
    """
    return Session()


def discard_db_session(exception=None):
    """
    The Session registry is instructed to remove the db session (if present):

    Session.remove():
      - calls Session.close() on the current Session
      (connection is returned to the connection pool and any transactional state is rolled back)
      - discards the Session itself.
    """
    Session.remove()


def add_db_session():
    """
    'before_request' handler.
    Add the request-local db session to g object for easier access.
    """
    g.db = get_db_session()


def remove_db_session(exception=None):
    """
    'teardown_request' handler.
    Add the request-local db session to g object for easier access.
    """
    if exception:
        g.db.rollback() # If no transaction is in progress, this method is a pass-through.
    g.db = None


def init_db():
    """
    Create new tables if they don't exist yet.
    """
    db = get_db_session()
    engine = db.bind
    Base.metadata.create_all(db.bind)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Create new tables if they don't exist yet.
    CLI command.
    """
    init_db()
    click.echo('Initialized the database.')



def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



def init_app(app):
    """
    Configure database binding, establish session registry, register handlers.
    """
    global Session, Base

    engine = create_engine(app.config["DATABASE_URI"], echo=app.config["SQLALCHEMY_ECHO"])
    Session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=False))
    Base.query = Session.query_property()

    if app.config["DATABASE_URI"].startswith("sqlite"):
        listen(Engine, "connect", set_sqlite_pragma)

    app.before_request(add_db_session)
    app.teardown_request(remove_db_session)
    app.teardown_appcontext(discard_db_session)
    app.cli.add_command(init_db_command)
