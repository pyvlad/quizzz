import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
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
        return "<Round (%r) of (%r) at (%r)>" % (self.id, self.quiz_id, self.tounament_id)
