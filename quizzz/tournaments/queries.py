from sqlalchemy.orm import joinedload
from flask import g, abort

from quizzz.auth.models import User
from quizzz.quizzes.models import Quiz, Question

from .models import Tournament, Round, Play, PlayAnswer



def query_tournament_by_id(tournament_id, with_rounds=False, with_plays=False, abort_if_none=True):
    """
    Query tournament data by <tournament_id>.
    Optionally loads related <Round>, round's <Quiz> and quiz author's <User> objects.
    By default, aborts and returns 404 error view if tournament does not exist.

    Returns: <tournament> ORM object, or None if not found and "abort_if_none" is set to False.
    """
    q = g.db.query(Tournament).filter(Tournament.id == tournament_id)
    if with_rounds:
        q = q.options(joinedload(Tournament.rounds).joinedload(Round.quiz).joinedload(Quiz.author))
    if with_plays:
        q = q.options(joinedload(Tournament.rounds).joinedload(Round.plays).joinedload(Play.user))
        # alternatively: g.db.query(User.id, User.name).filter(User.id.in_(user_ids)).all()

    tournament = q.first()

    if abort_if_none and (tournament is None):
        abort(404, "Tournament does not exist.")

    return tournament



def query_round_by_id(round_id, with_questions=False, with_author=False,
        with_plays=False, with_play_answers=False, with_tournament=False, abort_if_none=True):
    """
    Query round data by <round_id>.
    Optionally loads related objects.
    By default, aborts and returns 404 error view if round does not exist.

    Returns: <round> ORM object, or None if not found and "abort_if_none" is set to False.
    """
    q = g.db.query(Round).filter(Round.id == round_id)
    if with_questions:
        q = q.options(joinedload(Round.quiz).joinedload(Quiz.questions).joinedload(Question.options))
    if with_author:
        q = q.options(joinedload(Round.quiz).joinedload(Quiz.author))
    if with_plays:
        q = q.options(joinedload(Round.plays).joinedload(Play.user))
    if with_play_answers:
        q = q.options(joinedload(Round.plays).joinedload(Play.answers))
    if with_tournament:
        q = q.options(joinedload(Round.tournament))

    round = q.first()

    if abort_if_none and (round is None):
        abort(404, "This round does not exist.")

    return round



def query_play(round_id, user_id, with_answers=False, abort_if_none=True):
    """
    Query played quiz round data by <round_id> for specific <user_id>.
    Optionally loads related objects.
    By default, aborts and returns 404 error view if round does not exist.

    Returns: <play> ORM object, or None if not found and "abort_if_none" is set to False.
    """
    q = g.db.query(Play)\
        .filter(Play.round_id == round_id)\
        .filter(Play.user_id == user_id)
    if with_answers:
        q = q.options(joinedload(Play.answers).joinedload(PlayAnswer.option))

    play = q.first()

    if abort_if_none and (play is None):
        abort(404, "This user has not played this round.")

    return play



def query_quiz_pool(group_id):
    """
    Query quiz pool for specific group.
    Returns a list of (<quiz>, <author_id>, <author_name>) tuples
    with all finalized quizzes without a designated round, ordered by time_created.
    """
    return g.db.query(Quiz, User.id, User.name)\
        .join(User, Quiz.author_id == User.id)\
        .filter(Quiz.group_id == group_id)\
        .filter(Quiz.is_finalized == True)\
        .filter(Quiz.round == None)\
        .order_by(Quiz.time_created.desc())\
        .all()
