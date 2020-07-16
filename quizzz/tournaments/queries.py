from sqlalchemy.orm import joinedload
from flask import g, abort

from quizzz.auth.models import User
from quizzz.quizzes.models import Quiz, Question

from .models import Tournament, Round, Play, PlayAnswer



def get_tournament_by_id(tournament_id, with_rounds=False):
    if with_rounds:
        tournament = g.db.query(Tournament)\
            .options(joinedload(Tournament.rounds).joinedload(Round.quiz).joinedload(Quiz.author))\
            .filter(Tournament.id == tournament_id)\
            .first()
    else:
        tournament = g.db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if tournament is None:
        abort(404, "Tournament doesn't exist.")

    return tournament


def get_tournament_standings(tournament_id):
    tournament = g.db.query(Tournament)\
        .options(joinedload(Tournament.rounds).joinedload(Round.plays))\
        .filter(Tournament.id == tournament_id)\
        .first()

    if tournament is None:
        abort(404, "Tournament doesn't exist.")

    total_points = {}
    total_plays = {}
    for round in tournament.rounds:
        round_plays = [{"user_id": play.user_id, "score": play.get_score()} for play in round.plays]
        num_participants = len(round_plays)
        round_plays = sorted(round_plays, key=lambda x: x["score"], reverse=True)
        for i, round_play in enumerate(round_plays):
            user_id = round_play["user_id"]
            round_points = num_participants - i
            total_plays[user_id] = total_plays.get(user_id, 0) + 1
            total_points[user_id] = total_points.get(user_id, 0) + round_points

    standings = [
        {"user_id": x[0], "points": x[1], "rounds": total_plays[x[0]]}
        for x in sorted(total_points.items(), key=lambda x:x[1], reverse=True)
    ]

    user_ids = [x["user_id"] for x in standings]
    usernames_by_id = dict(g.db.query(User.id, User.name).filter(User.id.in_(user_ids)).all())

    for row in standings:
        row["user"] = usernames_by_id[row["user_id"]]

    return standings


def get_usernames(user_list):
    return


def get_round_by_id(round_id):
    round = g.db.query(Round).filter(Round.id == round_id).first()
    if not round:
        abort(404, "Round doesn't exist.")
    return round



def get_round_with_quiz_by_id(round_id):
    round = g.db.query(Round)\
        .options(joinedload(Round.quiz).joinedload(Quiz.questions).joinedload(Question.options))\
        .filter(Round.id == round_id)\
        .first()

    if round is None:
        abort(404, "No quiz available for this round.")

    return round



def get_round_with_details_by_id(round_id):
    round = g.db.query(Round)\
        .options(joinedload(Round.quiz).joinedload(Quiz.author))\
        .options(joinedload(Round.tournament))\
        .options(joinedload(Round.plays).joinedload(Play.user))\
        .filter(Round.id == round_id)\
        .first()

    if round is None:
        abort(404, "This round doesn't exist.")

    return round



def get_play_by_round_id(round_id, with_answers=False):
    if with_answers:
        play = g.db.query(Play)\
            .options(joinedload(Play.answers).joinedload(PlayAnswer.option))\
            .filter(Play.round_id == round_id)\
            .filter(Play.user_id == g.user.id)\
            .first()
    else:
        play = g.db.query(Play)\
            .filter(Play.round_id == round_id)\
            .filter(Play.user_id == g.user.id)\
            .first()

    return play



def get_quiz_pool(group_id):
    quiz_pool = g.db.query(Quiz, User.id, User.name)\
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
    user_plays = g.db.query(Play.round_id)\
        .join(Round, Play.round_id == Round.id)\
        .filter(Play.user_id == g.user.id)\
        .filter(Round.tournament_id == tournament_id)\
        .all()
    played_rounds = set(row.round_id for row in user_plays)

    return played_rounds
