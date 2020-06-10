from sqlalchemy.orm import joinedload
from flask import g, abort

from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.quizzes.models import Quiz, Question

from .models import Tournament, Round, Play, PlayAnswer



def get_tournament_by_id(tournament_id, with_rounds=False):
    db = get_db_session()

    if with_rounds:
        tournament = db.query(Tournament)\
            .options(joinedload(Tournament.rounds).joinedload(Round.quiz).joinedload(Quiz.author))\
            .filter(Tournament.id == tournament_id)\
            .first()
    else:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if tournament is None:
        abort(404, "Tournament doesn't exist.")

    return tournament



def get_round_by_id(round_id):
    db = get_db_session()
    round = db.query(Round).filter(Round.id == round_id).first()
    if not round:
        abort(404, "Round doesn't exist.")
    return round



def get_round_with_quiz_by_id(round_id):
    db = get_db_session()

    round = db.query(Round)\
        .options(joinedload(Round.quiz).joinedload(Quiz.questions).joinedload(Question.options))\
        .filter(Round.id == round_id)\
        .first()

    if round is None:
        abort(404, "No quiz available for this round.")

    return round



def get_round_with_details_by_id(round_id):
    db = get_db_session()

    round = db.query(Round)\
        .options(joinedload(Round.quiz).joinedload(Quiz.author))\
        .options(joinedload(Round.tournament))\
        .options(joinedload(Round.plays).joinedload(Play.user))\
        .filter(Round.id == round_id)\
        .first()

    if round is None:
        abort(404, "This round doesn't exist.")

    return round



def get_play_by_round_id(round_id, with_answers=False):
    db = get_db_session()

    if with_answers:
        play = db.query(Play)\
            .options(joinedload(Play.answers).joinedload(PlayAnswer.option))\
            .filter(Play.round_id == round_id)\
            .filter(Play.user_id == g.user.id)\
            .first()
    else:
        play = db.query(Play)\
            .filter(Play.round_id == round_id)\
            .filter(Play.user_id == g.user.id)\
            .first()

    return play



def get_quiz_pool(group_id):
    db = get_db_session()

    quiz_pool = db.query(Quiz, User.id, User.name)\
        .join(User, Quiz.author_id == User.id)\
        .filter(Quiz.group_id == group_id)\
        .filter(Quiz.is_finalized == True)\
        .filter(Quiz.round == None)\
        .order_by(Quiz.time_created.desc())\
        .all()

    return quiz_pool



def get_played_rounds_by_tournament_id(tournament_id):
    """
    Get set of round ids played by current user in given tournament.
    """
    db = get_db_session()

    user_plays = db.query(Play.round_id)\
        .join(Round, Play.round_id == Round.id)\
        .filter(Play.user_id == g.user.id)\
        .filter(Round.tournament_id == tournament_id)\
        .all()
    played_rounds = set(row.round_id for row in user_plays)

    return played_rounds
