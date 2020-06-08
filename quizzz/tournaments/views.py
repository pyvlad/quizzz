import traceback

from sqlalchemy.orm import joinedload
from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.db import get_db_session
from quizzz.permissions import USER, check_user_permissions
from quizzz.auth.models import User
from quizzz.quizzes.models import Quiz

from . import bp
from .models import Tournament, Round



# *** HELPERS ***
def get_tournament_by_id(tournament_id, with_rounds=False):
    db = get_db_session()

    if with_rounds:
        tournament = db.query(Tournament)\
            .options(joinedload(Tournament.rounds).joinedload(Round.quiz))\
            .filter(Tournament.id == tournament_id)\
            .first()
    else:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if tournament is None:
        abort(404, "Tournament doesn't exist.")

    return tournament


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



# *** VIEWS ***
@bp.route('/')
def index():
    """
    Get list of group tournaments.
    """
    data = {
        "tournaments": [
            {
                "id": tournament.id,
                "name": tournament.name
            }
            for tournament in g.group.tournaments
        ],
        "has_edit_permissions": g.group_membership.is_admin
    }
    return render_template('tournaments/index.html', data=data)



@bp.route('/<int:tournament_id>/edit', methods=('GET', 'POST'))
def edit_tournament(tournament_id):
    """
    Edit group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = (Tournament() if not tournament_id else get_tournament_by_id(tournament_id))

    if request.method == 'POST':
        tournament.populate_from_request_form(request.form)

        db = get_db_session()
        try:
            db.add(tournament)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Tournament could not be created!")
        else:
            flash("Tournament successfully created/updated.")
            return redirect(url_for('tournaments.show_tournament', tournament_id=tournament.id))

    data = {
        "tournament": {
            "id": tournament.id,
            "name": tournament.name,
            "has_started": tournament.has_started,
            "has_finished": tournament.has_finished
        }
    }

    return render_template('tournaments/edit.html', data=data)



@bp.route('/<int:tournament_id>/delete', methods=('POST',))
def delete_tournament(tournament_id):
    """
    Delete group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = get_tournament_by_id(tournament_id)

    db = get_db_session()
    db.delete(tournament)
    db.commit()
    flash("Tournament has been deleted.")

    return redirect(url_for('tournaments.index'))



@bp.route('/<int:tournament_id>/')
def show_tournament(tournament_id):
    """
    Show tournament details.
    """
    tournament = get_tournament_by_id(tournament_id, with_rounds=True)

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
                    "start_time": round.start_time or "",
                    "finish_time": round.finish_time or "",
                    "is_taken": round.quiz.id in { play.quiz_id for play in g.user.plays }
                }
                for round in tournament.rounds
            ]
        },
        "has_edit_permissions": g.group_membership.is_admin
    }

    return render_template('tournaments/tournament.html', data=data)






@bp.route('/rounds/<int:round_id>/')
def show_round(round_id):
    """
    Show round details.
    """
    check_user_permissions(USER.IS_GROUP_MEMBER)

    db = get_db_session()
    round = db.query(Round)\
        .options(joinedload(Round.quiz).joinedload(Quiz.author))\
        .options(joinedload(Round.tournament))\
        .filter(Round.id == round_id)\
        .first()
    if not round:
        abort(404, "This round doesn't exist.")

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



@bp.route("/<int:tournament_id>/rounds/<int:round_id>/edit", methods=("GET", "POST"))
def edit_round(tournament_id, round_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = get_tournament_by_id(tournament_id)
    quiz_pool = get_quiz_pool(g.group_id)

    db = get_db_session()

    if round_id:
        round = db.query(Round).filter(Round.id == round_id).first()
        if not round:
            abort(404, "Round doesn't exist.")
    else:
        round = Round()

    if request.method == 'POST':
        round.populate_from_request_form(request.form, tournament_id)

        try:
            db.add(round)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz Round could not be updated!")
        else:
            flash("Quiz Round has been created/updated.")
            return redirect(url_for('tournaments.show_tournament', tournament_id=tournament_id))

    data = {
        "tournament": {
            "id": tournament.id,
            "name": tournament.name
        },
        "quiz_pool": [{
            "id": quiz.id,
            "topic": quiz.topic,
            "author_name": author_name
        } for quiz, author_id, author_name in quiz_pool],
        "round": {
            "id": round.id,
            "start_time": round.start_time,
            "finish_time": round.finish_time,
            "quiz": {
                "id": round.quiz.id,
                "topic": round.quiz.topic,
                "author_name": round.quiz.author.name
            } if round.quiz else None
        }
    }

    return render_template('tournaments/edit_round.html', data=data)



@bp.route('/rounds/<int:round_id>/delete', methods=('POST',))
def delete_round(round_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    db = get_db_session()
    round = db.query(Round).filter(Round.id == round_id).first()
    if round:
        db.delete(round)
        flash("Quiz round has been deleted.")
    else:
        abort(404, "Quiz round doesn't exist.")
    db.commit()

    return redirect(url_for('tournaments.index'))
