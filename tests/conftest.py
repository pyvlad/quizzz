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

from quizzz.auth.models import User
from quizzz.groups.models import Group, Member
from quizzz.chat.models import Message
from quizzz.quiz.models import Quiz, Question, Option

from . import data


@pytest.fixture
def app():
    """ Calls the factory and configures the application for testing. """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE_URI': 'sqlite:///' + db_path,
        'SQLALCHEMY_ECHO': False
    })

    with app.app_context():
        init_db()

        objects = [
            *[User.from_credentials(**user) for user in data.USERS.values()],
            *[Group(**group) for group in data.GROUPS.values()],
            *[Member(**member) for member in data.MEMBERSHIPS],
            *[Message(**message) for message in data.MESSAGES],
            *[Quiz(**quiz) for quiz in data.QUIZZES.values()],
            *[Question(**question) for question in data.QUIZ_QUESTIONS.values()],
            *[Option(**option) for option in data.QUESTION_OPTIONS]
        ]

        db = get_db_session()
        db.add_all(objects)
        db.commit()

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


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username, password):
        return self._client.post('/auth/login', data={'username': username, 'password': password})

    def login_as(self, username):
        return self.login(data.USERS[username]["name"], data.USERS[username]["password"])

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """
    With the auth fixture, you can call auth.login() in a test to log in
    as the test user, which was inserted as part of the test data in the app fixture.
    """
    return AuthActions(client)
