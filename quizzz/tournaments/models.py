import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask import g, request

from quizzz.db import Base



class Tournament(Base):
    __tablename__ = "tournaments"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False)
    has_started = sa.Column(sa.Boolean, default=False)
    has_finished = sa.Column(sa.Boolean, default=False)
    time_created = sa.Column(sa.DateTime, server_default=func.now())

    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    group = relationship("Group", back_populates="tournaments")
    rounds = relationship("Round", back_populates="tournament",
        cascade="all, delete-orphan", order_by="Round.finish_time.desc()")

    def __repr__(self):
        return "<Tournament (%r) in (%r)>" % (self.name, self.group_id)

    def populate_from_wtform(self, form):
        self.group = g.group

        self.name = form.tournament_name.data
        self.has_started = bool(form.has_started.data)
        self.has_finished = bool(form.has_finished.data)

        return self



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
        return "<Round (%r) of (%r) at (%r)>" % (self.id, self.quiz_id, self.tournament_id)

    def populate_from_wtform(self, form, tournament_id):
        self.tournament_id = tournament_id
        self.quiz_id = form.quiz_id.data
        self.start_time = datetime.datetime.combine(form.start_date.data, datetime.datetime.min.time()) \
            + datetime.timedelta(hours=form.start_time_hours.data) \
            + datetime.timedelta(minutes=form.start_time_minutes.data)
        self.finish_time = datetime.datetime.combine(form.finish_date.data, datetime.datetime.min.time()) \
            + datetime.timedelta(hours=form.finish_time_hours.data) \
            + datetime.timedelta(minutes=form.finish_time_minutes.data)
        return self



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
    round_id = sa.Column(sa.Integer, sa.ForeignKey('rounds.id', ondelete='CASCADE'), nullable=False)

    user = relationship("User", back_populates="plays")
    round = relationship("Round", back_populates="plays")
    answers = relationship("PlayAnswer", back_populates="play", cascade="all, delete-orphan",
        passive_deletes=True)

    def __repr__(self):
        return "<RoundPlayed %r by %r>" % (self.round_id, self.user_id)

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

    def populate_from_wtform(self, form):
        quiz = self.round.quiz

        answers = []
        for qnum, question in enumerate(quiz.questions):
            options_by_id = { str(option.id): option for option in question.options }

            selected_option_id = form.questions[qnum].form.answer.data  # string
            selected_option = options_by_id.get(selected_option_id)

            answers += [PlayAnswer(play=self, option=selected_option)]

        self.answers = answers
        self.is_submitted = True
        self.result = len([answer for answer in answers if answer.option.is_correct])

        return self



class PlayAnswer(Base):
    __tablename__ = "answers"

    id = sa.Column(sa.Integer, primary_key=True)

    play_id = sa.Column(sa.Integer, sa.ForeignKey('plays.id', ondelete='CASCADE'), nullable=False)
    option_id = sa.Column(sa.Integer, sa.ForeignKey('options.id'), nullable=False)

    play = relationship("Play", back_populates="answers")
    option = relationship("Option", back_populates="answers")

    def __repr__(self):
        return "<AnswerSelected [%r] %r by %r>" % (
            "V" if self.option.is_correct else "X", self.option.text, self.play.user.name)
