import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from quizzz.db import Base
from flask import current_app, g


class Quiz(Base):
    __tablename__ = 'quizzes'

    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String(100), nullable=False)
    is_finalized = sa.Column(sa.Boolean, default=False)

    created = sa.Column(sa.DateTime, server_default=func.now())
    updated = sa.Column(sa.DateTime, onupdate=func.now())

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    author = relationship("User", backref="quizzes")
    group = relationship("Group", backref="quizzes")

    def __repr__(self):
        return "<Quiz (%r) by (%r)>" % (self.topic, self.author.name)

    @classmethod
    def from_request_form(cls, request_form):
        quiz = cls(topic=request_form['quiz_topic'], author=g.user, group=g.group)

        questions = []
        for qnum in range(1, current_app.config["QUESTIONS_PER_QUIZ"] + 1):
            question = Question(
                text=request_form['question_%s' % qnum],
                quiz=quiz
            )

            options = []
            for optnum in range(1, current_app.config["OPTIONS_PER_QUESTION"] + 1):
                options += [Option(
                    text=request_form['question_%s_option_%s' % (qnum, optnum)],
                    is_correct=(request_form['question_%s_answer' % qnum] == str(optnum)),
                    question=question
                )]

        return quiz


class Question(Base):
    __tablename__ = 'questions'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(1000), nullable=False)
    comment = sa.Column(sa.String(1000))

    created = sa.Column(sa.DateTime, server_default=func.now())
    updated = sa.Column(sa.DateTime, onupdate=func.now())

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id'), nullable=False)
    quiz = relationship("Quiz", backref=backref("questions", cascade="all, delete-orphan"))

    def __repr__(self):
        return "<Question (%r) from quiz id (%r)>" % (self.text[:20], self.quiz_id)


class Option(Base):
    __tablename__ = 'options'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(100), nullable=False)
    is_correct = sa.Column(sa.Boolean, nullable=False, default=False)

    created = sa.Column(sa.DateTime, server_default=func.now())
    updated = sa.Column(sa.DateTime, onupdate=func.now())

    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id'), nullable=False)
    question = relationship("Question", backref=backref("options", cascade="all, delete-orphan"))

    def __repr__(self):
        return "<Option (%r)%r>" % (self.text[:20], " (correct)" if self.is_correct else "")
