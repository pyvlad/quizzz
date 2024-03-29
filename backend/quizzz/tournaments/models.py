import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from quizzz.db import Base



class Tournament(Base):
    __tablename__ = "tournaments"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    is_active = sa.Column(sa.Boolean(name="is_active__bool"), default=False)
    time_created = sa.Column(sa.DateTime, server_default=func.now())

    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    group = relationship("Group", back_populates="tournaments")
    rounds = relationship("Round", back_populates="tournament",
        cascade="all, delete-orphan", order_by="Round.finish_time.desc()")

    def __repr__(self):
        return "<Tournament %r [%r]>" % (self.name, self.id)



class Round(Base):
    __tablename__ = 'rounds'

    id = sa.Column(sa.Integer, primary_key=True)

    start_time = sa.Column(sa.DateTime, nullable=False)
    finish_time = sa.Column(sa.DateTime, nullable=False)

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id'))
    tournament_id = sa.Column(sa.Integer, sa.ForeignKey('tournaments.id'))

    quiz = relationship("Quiz", back_populates="round")
    tournament = relationship("Tournament", back_populates="rounds")
    plays = relationship("Play", back_populates="round", cascade="all, delete-orphan",
        passive_deletes=True)
    messages = relationship("Message", back_populates="round", cascade="all, delete-orphan",
        passive_deletes=True)

    def __repr__(self):
        return "<Round [%r]>" % self.id

    @property
    def time_left(self):
        seconds_left = (self.finish_time - datetime.datetime.utcnow()).total_seconds()
        return {
            "days": int(seconds_left // (60 * 60 * 24)),
            "hours": int((seconds_left % (60 * 60 * 24)) // (60 * 60)),
            "minutes": int(((seconds_left % (60 * 60 * 24)) % (60 * 60)) // 60),
        }

    def get_status(self, now=None):
        if now is None:
            now = datetime.datetime.utcnow()
        if now < self.start_time:
            return "coming"
        elif now > self.finish_time:
            return "finished"
        else:
            return "current"

    @property
    def is_active(self):
        return self.get_status() == "current"

    def get_author_score(self):
        return len(self.plays)

    def is_authored_by(self, user_id):
        return self.quiz.author_id == user_id



class Play(Base):
    __tablename__ = "plays"

    id = sa.Column(sa.Integer, primary_key=True)

    is_submitted = sa.Column(sa.Boolean(name="is_submitted__bool"), default=False)
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
    round_id = sa.Column(sa.Integer, sa.ForeignKey('rounds.id', ondelete='CASCADE'), nullable=False)

    user = relationship("User", back_populates="plays")
    round = relationship("Round", back_populates="plays")
    answers = relationship("PlayAnswer", back_populates="play", cascade="all, delete-orphan",
        passive_deletes=True)

    def __repr__(self):
        return "<Play of %r by %r [%r]>" % (self.round_id, self.user.name, self.user_id)

    def get_server_time(self):
        if self.server_updated is None or self.server_started is None:
            return None
        return (self.server_updated - self.server_started).total_seconds()

    def get_client_time(self):
        if self.client_updated is None or self.client_started is None:
            return None
        return (self.client_updated - self.client_started).total_seconds()

    def get_result(self):
        return len([answer.option.is_correct for answer in self.answers])

    def get_score(self):
        if self.result and self.get_server_time():
            return max(0, 100 * self.result - self.get_server_time())
        else:
            return 0



class PlayAnswer(Base):
    __tablename__ = "answers"

    id = sa.Column(sa.Integer, primary_key=True)

    play_id = sa.Column(sa.Integer, sa.ForeignKey('plays.id', ondelete='CASCADE'), nullable=False)
    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id'), nullable=False)
    option_id = sa.Column(sa.Integer, sa.ForeignKey('options.id'))

    play = relationship("Play", back_populates="answers")
    option = relationship("Option", back_populates="answers")

    def __repr__(self):
        return "<AnswerSelected [%r]>" % self.id