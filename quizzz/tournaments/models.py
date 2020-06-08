import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
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
    group = relationship("Group", backref="tournaments")

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
    quiz = relationship("Quiz", backref=backref("round", uselist=False))

    tournament_id = sa.Column(sa.Integer, sa.ForeignKey('tournaments.id'))
    tournament = relationship("Tournament", backref=backref("rounds", cascade="all, delete-orphan"))

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
