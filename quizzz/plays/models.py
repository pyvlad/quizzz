import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
# from sqlalchemy.sql import func, text
from quizzz.db import Base
from flask import current_app, g


class Play(Base):
    __tablename__ = "plays"

    id = sa.Column(sa.Integer, primary_key=True)

    is_submitted = sa.Column(sa.Boolean, default=False)
    result = sa.Column(sa.Integer)
    server_started = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    server_updated = sa.Column(sa.DateTime, onupdate=datetime.datetime.utcnow)
    # alternative 1 (sqlite only):
    # server_started = sa.Column(sa.DateTime, server_default=text("(STRFTIME('%Y-%m-%d %H:%M:%f000', 'NOW'))"))
    # server_updated = sa.Column(sa.DateTime, onupdate=text("STRFTIME('%Y-%m-%d %H:%M:%f000', 'NOW')"))
    # alternative 2 (lacks precision):
    # server_started = sa.Column(sa.DateTime, server_default=func.now())
    # server_updated = sa.Column(sa.DateTime, onupdate=func.now())

    client_started = sa.Column(sa.DateTime)
    client_updated = sa.Column(sa.DateTime)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    user = relationship("User", backref="plays")

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id'), nullable=False)
    quiz = relationship("Quiz", backref="plays")

    def __repr__(self):
        return "<RoundPlayed %r by %r>" % (self.round_id, self.user_id)

    def get_server_time(self):
        return (self.server_updated - self.server_started).total_seconds()

    def get_client_time(self):
        return (self.client_updated - self.client_started).total_seconds()

    def get_result(self):
        return len(answer.option.is_correct for answer in self.answers)


class PlayAnswer(Base):
    __tablename__ = "answers"

    id = sa.Column(sa.Integer, primary_key=True)
    play_id = sa.Column(sa.Integer, sa.ForeignKey('plays.id'), nullable=False)
    option_id = sa.Column(sa.Integer, sa.ForeignKey('options.id'), nullable=False)

    play = relationship("Play", backref="answers")
    option = relationship("Option", backref="answers")

    def __repr__(self):
        return "<AnswerSelected [%r] %r by %r>" % (
            "V" if self.option.is_correct else "X", self.option.text, self.play.user.name)
