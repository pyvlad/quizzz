from flask import g, abort
from sqlalchemy.orm import joinedload

from quizzz.db import get_db_session

from .models import Quiz, Question, Option


def get_own_quiz_by_id(quiz_id, with_questions=False):
    db = get_db_session()

    if with_questions:
        quiz = db.query(Quiz)\
            .options(joinedload(Quiz.questions).joinedload(Question.options))\
            .filter(Quiz.id == quiz_id)\
            .first()
    else:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if quiz is None:
        abort(404, "Quiz doesn't exist.")
    if quiz.author_id != g.user.id:
        abort(403, "What do you think you're doing?")

    return quiz
