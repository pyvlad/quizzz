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

    time_created = sa.Column(sa.DateTime, server_default=func.now())
    time_updated = sa.Column(sa.DateTime, onupdate=func.now())

    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)

    author = relationship("User", back_populates="quizzes")
    group = relationship("Group", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    round = relationship("Round", back_populates="quiz", uselist=False)

    def __repr__(self):
        return "<Quiz (%r) by (%r)>" % (self.topic, self.author.name)

    def populate_from_request_form(self, request_form):
        self.author = g.user
        self.group = g.group

        self.topic = request_form['topic']
        self.is_finalized = True if request_form['is_finalized'] == '1' else False

        if not self.questions:
            self.init_questions()

        for qnum, question in enumerate(self.questions, 1):
            question.text = request_form['question_%s' % qnum]
            for optnum, option in enumerate(question.options, 1):
                option.text = request_form['question_%s_option_%s' % (qnum, optnum)]
                option.is_correct = (request_form['question_%s_answer' % qnum] == str(optnum))

        return self

    def init_questions(self):
        for qnum in range(1, current_app.config["QUESTIONS_PER_QUIZ"] + 1):
            question = Question(quiz=self)
            for optnum in range(1, current_app.config["OPTIONS_PER_QUESTION"] + 1):
                option = Option(question=question)



class Question(Base):
    __tablename__ = 'questions'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(1000), nullable=False)
    comment = sa.Column(sa.String(1000))

    quiz_id = sa.Column(sa.Integer, sa.ForeignKey('quizzes.id'), nullable=False)

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Question (%r) from quiz id (%r)>" % (self.text[:20], self.quiz_id)



class Option(Base):
    __tablename__ = 'options'

    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String(100), nullable=False)
    is_correct = sa.Column(sa.Boolean, nullable=False, default=False)

    question_id = sa.Column(sa.Integer, sa.ForeignKey('questions.id'), nullable=False)

    question = relationship("Question", back_populates="options")
    answers = relationship("PlayAnswer", back_populates="option")

    def __repr__(self):
        return "<Option (%r)%r>" % (self.text[:20], " (correct)" if self.is_correct else "")
