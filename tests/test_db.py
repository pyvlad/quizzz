import sqlite3

import pytest
from werkzeug.security import generate_password_hash
from quizzz.db import get_db_session
from quizzz.auth.models import User


def test_session_scope(app):
    with app.app_context():
        db_session = get_db_session()
        assert db_session is get_db_session()

    with app.app_context():
        assert db_session is not get_db_session()


def test_session_rollback_on_context_teardown(app):
    with app.app_context():
        db_session = get_db_session()
        res = db_session.query(User).all()
        assert len(res) == 2

    with app.app_context():
        db_session = get_db_session()
        db_session.add(User(name="dodgy", password_hash=generate_password_hash("secret")))
        res = db_session.query(User).all()
        assert len(res) == 3

    with app.app_context():
        db_session = get_db_session()
        db_session.commit()
        res = db_session.query(User).all()
        assert len(res) == 2


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
