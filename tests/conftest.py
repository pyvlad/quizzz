"""
The tests/conftest.py file contains setup functions
called fixtures that each test will use.

Tests are in Python modules that start with test_,
and each test function in those modules also starts with test_.

Pytest uses fixtures by matching their function names
with the names of arguments in the test functions.
"""
import os
import tempfile

import pytest
from quizzz import create_app
from quizzz.db import init_db, get_db_session
from quizzz.models import User


@pytest.fixture
def app():
    """ Calls the factory and configures the application for testing. """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE_URI': 'sqlite:///' + db_path,
    })

    with app.app_context():
        init_db()
        db_session = get_db_session()
        db_session.add_all([
            User(name="bob", email="bob@example.com"),
            User(name="alice", email="alice@example.com"),
        ])
        db_session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """ Creates a client to make requests to the application without running the server. """
    return app.test_client()


@pytest.fixture
def runner(app):
    """ Creates a runner that can call the Click commands registered with the application. """
    return app.test_cli_runner()
