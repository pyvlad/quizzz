from flask import g, flash, request, redirect, url_for, abort, render_template
from . import bp
from .models import Tournament, Round
from quizzz.db import get_db_session



@bp.route('/')
def index():
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if g.group.id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    data = {
        "tournaments": [
            {
                "id": tournament.id,
                "name": tournament.name
            }
            for tournament in g.group.tournaments
        ]
    }

    return render_template('tournaments/tournament_list.html', data=data)



@bp.route('/<int:tournament_id>/')
def show_tournament(tournament_id):
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if g.group.id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    db = get_db_session()
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        abort(404, "This tournament doesn't exist.")

    data = {
        "tournament": {
            "id": tournament.id,
            "name": tournament.name,
            "rounds": [
                {
                    "id": round.id,
                    "quiz": {
                        "id": round.quiz.id,
                        "topic": round.quiz.topic,
                        "author": round.quiz.author.name
                    },
                    "is_taken": round.quiz.id in { play.quiz_id for play in g.user.plays }
                }
                for round in tournament.rounds
            ]
        }
    }

    return render_template('tournaments/tournament.html', data=data)



@bp.route('/rounds/<int:round_id>/')
def show_round(round_id):
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if g.group.id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    db = get_db_session()
    round = db.query(Round).filter(Round.id == round_id).first()
    if not round:
        abort(404, "This tournament doesn't exist.")

    data = {
        "tournament": {
            "id": round.tournament.id,
            "name": round.tournament.name
        },
        "quiz": {
            "id": round.quiz.id,
            "topic": round.quiz.topic,
            "author": round.quiz.author.name,
            "plays": [
                {
                    "id": play.id,
                    "user": play.user.name,
                    "result": play.result,
                    "time": play.get_server_time()
                }
                for play in round.quiz.plays
            ]
        },
        "round": {
            "id": round.id,
        },
        "is_taken": g.user.id in { play.user.id for play in round.quiz.plays }
    }

    return render_template('tournaments/round.html', data=data)
