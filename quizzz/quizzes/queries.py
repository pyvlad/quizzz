from flask import g, abort
from sqlalchemy.orm import joinedload

from .models import Quiz, Question, Option


def query_quiz_by_id(quiz_id, with_questions=False, abort_if_none=True):
    """
    Query quiz data by <quiz_id>.
    Optionally loads related <Question>, question's <Option> objects.
    By default, aborts and returns 404 error view if quiz does not exist.

    Returns: <quiz> ORM object, or None if not found and "abort_if_none" is set to False.
    """
    q = g.db.query(Quiz).filter(Quiz.id == quiz_id)

    if with_questions:
        q = q.options(joinedload(Quiz.questions).joinedload(Question.options))

    quiz = q.first()

    if abort_if_none and (quiz is None):
        abort(404, "Quiz does not exist.")

    return quiz



def query_user_quizzes(user_id, group_id, which="all", return_count=False):
    """
    Query list of user's quizzes for <user_id> in <group_id>.
    <which> parameter lets you apply filters:
    - "finalized";
    - "in-progress";
    - "all" [default].

    Returns: list of <quiz> ORM objects, or None if not found and "abort_if_none" is set to False.
    Setting <return_count> to True will return number of quizzes, rather than a list of quiz objects.
    """
    query = g.db.query(Quiz)\
        .filter(Quiz.author_id == user_id)\
        .filter(Quiz.group_id == group_id)

    if which == "finalized":
        query = query.filter(Quiz.is_finalized == True)
    elif which == "in-progress":
        query = query.filter(Quiz.is_finalized != True)
    elif which == "all":
        pass
    else:
        raise ValueError("Unsupported values of 'which': %s" % which)

    if return_count:
        return query.count()
    else:
        return query.order_by(Quiz.time_created.desc()).all()
