import sqlite3

import pytest
from quizzz.db import get_db_session
from quizzz.auth.models import User

from .data import USERS


def test_session_scope(app):
    """
    <get_db_session> should return the same session object within one app_context.
    """
    with app.app_context():
        db = get_db_session()
        assert db is get_db_session()

    with app.app_context():
        assert db is not get_db_session()


def test_session_rollback_on_context_teardown(app):
    """
    Commit in a different app_context should not work.
    """
    with app.app_context():
        db = get_db_session()
        db.add(User.from_credentials(name="dodgy", password="secret"))
        res = db.query(User).all()
        assert len(res) == len(USERS) + 1

    with app.app_context():
        db = get_db_session()
        db.commit()
        res = db.query(User).all()
        assert len(res) == len(USERS)


def test_init_db_command(runner, monkeypatch):
    """
    The init-db command should call the init_db function and output a message.
    This test uses Pytest’s monkeypatch fixture to replace the init_db function
    with one that records that it’s been called.
    """
    class Recorder():
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('quizzz.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called
