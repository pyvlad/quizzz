"""
Create dev DB with some data.
"""
import datetime

import click
from flask.cli import with_appcontext

from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.groups.models import Group, Member
from quizzz.chat.models import Message
from quizzz.quizzes.models import Quiz, Question, Option
from quizzz.tournaments.models import Tournament, Round



def make_db_objects():
    # add some users
    bob = User.from_credentials(name="bob", password="dog", email="bob@example.com",
        is_confirmed=True, can_create_groups=True)
    alice = User.from_credentials(name="alice", password="cat", email="alice@example.com")

    # add some groups
    main_group = Group(
        name="Main",
        password="hello",
        members = [
            Member(user=bob, is_admin=True),
            Member(user=alice)
        ]
    )
    other_group = Group(name="Other")

    # add some messages to chat
    messages = [                    # pylint: disable=unused-variable
        Message(text="Hello, world!", user=bob, group=main_group),
        Message(text="This is a great chat!", user=alice, group=main_group),
        Message(text="Pretty lame. All I gotta say.", user=alice, group=main_group)
    ]

    # add a few quizzes
    quizzes = [
        Quiz(
            topic="Mixed Bag",
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
            author=bob,
            group=main_group,
            is_finalized=True
        ),
        Quiz(
            topic="Cities",
            questions=[
                Question(
                    text="What city is officially the capital of Russia?",
                    options=[
                        Option(text="Kiev"),
                        Option(text="Moscow", is_correct=True),
                        Option(text="Russianberg"),
                        Option(text="Saint Petersburg")
                    ]
                ),
                Question(
                    text="What city never was a capital of Russia?",
                    options=[
                        Option(text="Moscow"),
                        Option(text="Novgorod"),
                        Option(text="Kiev"),
                        Option(text="Novosibirsk", is_correct=True)
                    ]
                ),
            ],
            author=bob,
            group=other_group
        ),
        Quiz(
            topic="Programming",
            questions=[
                Question(
                    text="Which of these is a programming language?",
                    options=[
                        Option(text="Python", is_correct=True),
                        Option(text="Anaconda"),
                        Option(text="HTML"),
                        Option(text="CSS")
                    ]
                ),
                Question(
                    text="Which famous programmer didn't participate in the development of UNIX at Belle Labs?",
                    options=[
                        Option(text="Ken Thompson"),
                        Option(text="Dennis Ritchie"),
                        Option(text="Douglas McIlroy"),
                        Option(text="Guido van Rossum", is_correct=True)
                    ]
                ),
            ],
            author=bob,
            group=main_group
        ),
        Quiz(
            topic="Definitions of Things",
            questions=[
                Question(
                    text="What is love?",
                    options=[
                        Option(text="baby don't hurt me"),
                        Option(text="don't hurt me"),
                        Option(text="no more"),
                        Option(text="all of these", is_correct=True)
                    ]
                ),
                Question(
                    text="How much is the fish?",
                    options=[
                        Option(text="lala-lalala-la-la"),
                        Option(text="lalalala"),
                        Option(text="lala-lalala-la-lalala"),
                        Option(text="all of these", is_correct=True)
                    ]
                ),
            ],
            author=alice,
            group=main_group,
            is_finalized=True
        )
    ]
    for quiz in quizzes:
        quiz.num_questions = len(quiz.questions)
        quiz.num_options = len(quiz.questions[0].options)


    now = datetime.datetime.utcnow()
    now = now.replace(second=0, microsecond=0)
    tournament = Tournament(                        # pylint: disable=unused-variable
        name="First Tournament",
        group=main_group,
        rounds=[
            Round(quiz=quizzes[0], start_time=now, finish_time=now + datetime.timedelta(minutes=60)),
            Round(quiz=quizzes[3], start_time=(now + datetime.timedelta(minutes=5)),
                finish_time=(now + datetime.timedelta(days=7)))
        ],
        is_active=True
    )

    return [main_group, other_group]



@click.command('add-dev-data')
@with_appcontext
def add_dev_data():
    """
    Fill DB tables with some initial data for development.
    """
    db_session = get_db_session()
    user = db_session.query(User).filter(User.name == "bob").first()
    if user:
        click.echo('Fail! DB is already filled with initial data.')
    else:
        db_objects = make_db_objects()
        db_session.add_all(db_objects)
        db_session.commit()
        click.echo('Success! DB is created and filled with initial data.')
