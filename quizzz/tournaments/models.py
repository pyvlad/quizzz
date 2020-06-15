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

    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    group = relationship("Group", back_populates="tournaments")
    rounds = relationship("Round", back_populates="tournament", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Tournament (%r) in (%r)>" % (self.name, self.group_id)

    def populate_from_request_form(self, request_form):
        self.group = g.group

        self.name = request.form["tournament_name"]
        self.has_started = bool(request.form.get("has_started"))
        self.has_finished = bool(request.form.get("has_finished"))

        return self



class Round(Base):
    __tablename__ = 'rounds'

    id = sa.Column(sa.Integer, primary_key=True)

    start_time = sa.Column(sa.DateTime)
    finish_time = sa.Column(sa.DateTime)

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id'))
    tournament_id = sa.Column(sa.Integer, sa.ForeignKey('tournaments.id'))

    quiz = relationship("Quiz", back_populates="round")
    tournament = relationship("Tournament", back_populates="rounds")
    plays = relationship("Play", back_populates="round")
    messages = relationship("Message", back_populates="round")

    def __repr__(self):
        return "<Round (%r) of (%r) at (%r)>" % (self.id, self.quiz_id, self.tournament_id)

    def populate_from_request_form(self, request_form, tournament_id):
        self.tournament_id = tournament_id
        self.quiz_id = int(request.form["quiz_id"])
        if request.form.get("start_time"):
            self.start_time = datetime.datetime.strptime(request.form["start_time"], '%Y-%m-%d')
        if request.form.get("finish_time"):
            self.finish_time = datetime.datetime.strptime(request.form["finish_time"], '%Y-%m-%d')
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
    round_id = sa.Column(sa.Integer, sa.ForeignKey('rounds.id'), nullable=False)

    user = relationship("User", back_populates="plays")
    round = relationship("Round", back_populates="plays")
    answers = relationship("PlayAnswer", back_populates="play")

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
        return len(answer.option.is_correct for answer in self.answers)

    def populate_from_request_form(self, request_form):
        quiz = self.round.quiz

        answers = []
        for question in quiz.questions:
            options_by_id = { option.id: option for option in question.options }

            selected_option_id = int(request.form["q%s" % question.id])
            selected_option = options_by_id.get(selected_option_id)

            answers += [PlayAnswer(play=self, option=selected_option)]

        self.answers = answers
        self.is_submitted = True
        self.result = len([answer for answer in answers if answer.option.is_correct])

        return self



class PlayAnswer(Base):
    __tablename__ = "answers"

    id = sa.Column(sa.Integer, primary_key=True)

    play_id = sa.Column(sa.Integer, sa.ForeignKey('plays.id'), nullable=False)
    option_id = sa.Column(sa.Integer, sa.ForeignKey('options.id'), nullable=False)

    play = relationship("Play", back_populates="answers")
    option = relationship("Option", back_populates="answers")

    def __repr__(self):
        return "<AnswerSelected [%r] %r by %r>" % (
            "V" if self.option.is_correct else "X", self.option.text, self.play.user.name)
