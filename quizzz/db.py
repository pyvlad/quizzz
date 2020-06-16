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


def close_db_session(exception=None):
    """
    The Session registry is instructed to remove the db session (if present):

    Session.remove():
      - calls Session.close() on the current Session
      (connection is returned to the connection pool and any transactional state is rolled back)
      - discards the Session itself.
    """
    Session.remove()


def init_db():
    """ """
    engine = create_engine(current_app.config["DATABASE_URI"])
    Base.metadata.create_all(engine)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Create new tables if they don't exist yet.
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

    app.teardown_appcontext(close_db_session)
    app.cli.add_command(init_db_command)
