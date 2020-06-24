import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask import current_app, g

from quizzz.db import Base


class Quiz(Base):
    __tablename__ = 'quizzes'

    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String(100), nullable=False)
    is_finalized = sa.Column(sa.Boolean, default=False)

    num_questions = sa.Column(sa.Integer, default=0, nullable=False)
    num_options = sa.Column(sa.Integer, default=4, nullable=False)

    time_created = sa.Column(sa.DateTime, server_default=func.now())
    time_updated = sa.Column(sa.DateTime, onupdate=func.now())

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    author = relationship("User", back_populates="quizzes")
    group = relationship("Group", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan",
        passive_deletes=True)
    round = relationship("Round", back_populates="quiz", uselist=False)

    def __repr__(self):
        return "<Quiz (%r) by (%r)>" % (self.topic, self.author.name)

    def init_questions(self):
        for i in range(self.num_questions):
            question = Question(quiz=self)
            for j in range(self.num_options):
                option = Option(question=question)

    def populate_from_wtform(self, form):
        self.author = g.user
        self.group = g.group

        self.topic = form.topic.data
        self.is_finalized = True if form.is_finalized.data == '1' else False

        if not self.questions:
            self.init_questions()

        for qnum, question in enumerate(self.questions):
            question_subform = form.questions[qnum].form
            question.text = question_subform.text.data
            for optnum, option in enumerate(question.options):
                option.text = question_subform.options[optnum].form.text.data
                option.is_correct = (question_subform.answer.data == str(optnum))


class Question(Base):
    __tablename__ = 'questions'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(1000), nullable=False)
    comment = sa.Column(sa.String(1000))

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan",
        passive_deletes=True)

    def __repr__(self):
        return "<Question (%r) from quiz id (%r)>" % (self.text[:20], self.quiz_id)



class Option(Base):
    __tablename__ = 'options'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(100), nullable=False)
    is_correct = sa.Column(sa.Boolean, nullable=False, default=False)

    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)

    question = relationship("Question", back_populates="options")
    answers = relationship("PlayAnswer", back_populates="option")

    def __repr__(self):
        return "<Option (%r)%r>" % (self.text[:20], " (correct)" if self.is_correct else "")
