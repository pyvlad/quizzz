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
from werkzeug.security import generate_password_hash
from quizzz import create_app
from quizzz.db import init_db, get_db_session
from quizzz.auth.models import User
from quizzz.groups.models import Group, Member
from quizzz.chat.models import Message
from quizzz.quiz.models import Quiz, Question, Option


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
        db_session = get_db_session()

        # add some users
        bob = User(name="bob", password_hash=generate_password_hash("dog"))
        alice = User(name="alice", password_hash=generate_password_hash("cat"))

        # add some groups
        group1 = Group(
            name="group1",
            invitation_code="code1",
            members = [
                Member(user=bob, is_admin=True),
                Member(user=alice)
            ]
        )
        group2 = Group(
            name="group2",
            invitation_code="no",
            members=[
                Member(user=alice)
            ]
        )

        # add some messages
        messages = [
            Message(text="hello from bob", user=bob, group=group1, id=1),
            Message(text="hello from alice", user=alice, group=group1, id=2),
            Message(text="hello again from alice", user=alice, group=group2, id=3)
        ]

        # add a quiz
        quiz = Quiz(
            topic="Test Quiz",
            questions=[
                Question(
                    text="What does 2+2 equal to?",
                    comment="That's a toughie. But you can verify the answer with your fingers.",
                    options=[
                        Option(text="1"),
                        Option(text="2"),
                        Option(text="3"),
                        Option(text="4", is_correct=True)
                    ]
                ),
                Question(
                    text="What does the fox say?",
                    comment="Try searching the answer on youtube.",
                    options=[
                        Option(text="Meaow"),
                        Option(text="Woof"),
                        Option(text="Bazinga!"),
                        Option(text="None of these", is_correct=True)
                    ]
                ),
            ],
            author=alice,
            group=group1
        )
        db_session.add_all([bob, alice])
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


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='alice', password='cat'):
        return self._client.post('/auth/login', data={'username': username, 'password': password})

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """
    With the auth fixture, you can call auth.login() in a test to log in
    as the test user, which was inserted as part of the test data in the app fixture.
    """
    return AuthActions(client)
