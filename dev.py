"""
Create dev DB with some data.
"""
from werkzeug.security import generate_password_hash
from quizzz.db import init_db, get_db_session
from quizzz.auth.models import User
from quizzz.chat.models import Message
from quizzz.quiz.models import Quiz, Question, Option
from quizzz import create_app


app = create_app()
with app.app_context():
    init_db()
    db_session = get_db_session()

    # add some users
    bob = User(name="bob", password_hash=generate_password_hash("dog"))
    alice = User(name="alice", password_hash=generate_password_hash("cat"))

    # add some messages to chat
    messages = [
        Message(text="Hello, world!", user=bob),
        Message(text="This is a great chat!", user=alice),
        Message(text="Pretty lame. All I gotta say.", user=alice)
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
            author=bob
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
            author=bob
        ),
        Quiz(
            topic="Cities",
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
            author=bob
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
            author=alice
        )
    ]

    db_session.add_all([bob, alice])
    db_session.commit()
