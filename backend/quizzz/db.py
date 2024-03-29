import click
from flask import current_app, g
from flask.cli import with_appcontext
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.event import listen
from sqlalchemy.inspection import inspect


# The Importance of Naming Constraints
# https://alembic.sqlalchemy.org/en/latest/naming.html
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",    # e.g. booleans for SQLite must be named
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})
Base = declarative_base(metadata=metadata)
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


# This is used in tests.
def init_db():
    """
    Create DB tables if they don't exist yet.
    """
    db = get_db_session()
    engine = db.bind
    Base.metadata.create_all(engine)


# this command is replaced with migrations
# @click.command('init-db')
# @with_appcontext
# def init_db_command():
#     """
#     Create DB tables if they don't exist yet.
#     """
#     init_db()
#     click.echo('Initialized the database.')



def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



def instant_defaults_listener(target, args, kwargs):
    """
    https://stackoverflow.com/questions/14002631/why-isnt-sqlalchemy-default-column-value-available-before-object-is-committed/48097586
    """
    for key, column in inspect(target.__class__).columns.items():
        if column.default is not None:
            if callable(column.default.arg):
                setattr(target, key, column.default.arg(target))
            else:
                setattr(target, key, column.default.arg)



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
    listen(mapper, 'init', instant_defaults_listener)

    app.before_request(add_db_session)
    app.teardown_request(remove_db_session)
    app.teardown_appcontext(discard_db_session)
    # app.cli.add_command(init_db_command)


class TimeStampedModel:
    time_created = sa.Column(sa.DateTime, server_default=func.now())
    time_updated = sa.Column(sa.DateTime, onupdate=func.now())
    # The declarative extension creates a copy of each Column object 
    # encountered on a class that is detected as a mixin
    # There’s no fixed convention over whether a mixin precedes Base or not. 
    # Normal Python method resolution rules apply
    # source: https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html