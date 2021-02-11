import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask import current_app, g

from quizzz.db import Base, TimeStampedModel


class Quiz(TimeStampedModel,Base):
    __tablename__ = 'quizzes'

    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String(100), default="Anonymous Quiz")
    is_finalized = sa.Column(sa.Boolean(name="is_finalized__bool"), default=False)

    num_questions = sa.Column(sa.Integer, default=0, nullable=False)
    num_options = sa.Column(sa.Integer, default=4, nullable=False)

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    author = relationship("User", back_populates="quizzes")
    group = relationship("Group", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan",
        passive_deletes=True)
    round = relationship("Round", back_populates="quiz", uselist=False)

    def __repr__(self):
        return "<Quiz: %r [%r]>" % (self.topic[:20], self.id)

    def init_questions(self):
        for _ in range(self.num_questions):             
            question = Question(quiz=self)
            for _ in range(self.num_options):
                option = Option(question=question)  # pylint: disable=unused-variable



class Question(Base):
    __tablename__ = 'questions'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(1000), default="")
    comment = sa.Column(sa.String(1000))

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan",
        passive_deletes=True)

    def __repr__(self):
        return "<Question: %r [%r]>" % (self.text[:20], self.id)



class Option(Base):
    __tablename__ = 'options'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(100), default="")
    is_correct = sa.Column(sa.Boolean(name="is_correct__bool"), nullable=False, default=False)

    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)

    question = relationship("Question", back_populates="options")
    answers = relationship("PlayAnswer", back_populates="option")

    def __repr__(self):
        return "<Option %r [%r]>" % (
            self.text[:20] + (" (correct)" if self.is_correct else ""), self.id)
