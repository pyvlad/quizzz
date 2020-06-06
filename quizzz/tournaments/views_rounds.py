import traceback
import datetime

from flask import g, flash, request, redirect, url_for, abort, render_template
from . import bp
from .models import Tournament, Round
from .user_permissions import USER, check_user_permissions
from quizzz.db import get_db_session
from quizzz.quizzes.models import Quiz



@bp.route('/rounds/<int:round_id>/')
def show_round(round_id):
    """
    Show round details.
    """
    check_user_permissions(USER.IS_GROUP_MEMBER)

    db = get_db_session()
    round = db.query(Round).filter(Round.id == round_id).first()
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



@bp.route("/tournaments/<int:tournament_id>/create_round", methods=('GET', 'POST'))
def create_round(tournament_id):
    """
    Create new tournament round.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    db = get_db_session()
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        abort(404, "This tournament doesn't exist.")

    round = None

    group_quizzes = db.query(Quiz)\
        .filter(Quiz.group_id == g.group.id)\
        .order_by(Quiz.created.desc())\
        .all()
    quiz_pool = [q for q in group_quizzes if q.is_finalized and q.round is None]

    if request.method == 'POST':
        quiz_id = int(request.form["quiz_id"])
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

        round = Round()
        round.tournament = tournament
        round.quiz = quiz
        if request.form.get("start_time"):
            round.start_time = datetime.datetime.strptime(request.form["start_time"], '%Y-%m-%d')
        if request.form.get("finish_time"):
            round.finish_time = datetime.datetime.strptime(request.form["finish_time"], '%Y-%m-%d')

        try:
            db.add(round)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz Round could not be created!")
        else:
            flash("Quiz Round has been created.")
            return redirect(url_for('tournaments.index'))

    return render_template('tournaments/create_round.html',
        tournament=tournament, round=round, quiz_pool=quiz_pool)



@bp.route("/tournaments/<int:tournament_id>/update_round/<int:round_id>/", methods=('GET', 'POST'))
def update_round(tournament_id, round_id):
    """
    Create new group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    db = get_db_session()
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        abort(404, "Tournament doesn't exist.")

    round = db.query(Round).filter(Round.id == round_id).first()
    if not round:
        abort(404, "Round doesn't exist.")

    group_quizzes = db.query(Quiz)\
        .filter(Quiz.group_id == g.group.id)\
        .order_by(Quiz.created.desc())\
        .all()
    quiz_pool = [q for q in group_quizzes if q.is_finalized and q.round is None]

    if request.method == 'POST':
        quiz_id = int(request.form["quiz_id"])
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

        round.tournament = tournament
        round.quiz = quiz
        if request.form.get("start_time"):
            round.start_time = datetime.datetime.strptime(request.form["start_time"], '%Y-%m-%d')
        if request.form.get("finish_time"):
            round.finish_time = datetime.datetime.strptime(request.form["finish_time"], '%Y-%m-%d')

        try:
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz Round could not be updated!")
        else:
            flash("Quiz Round has been updated.")
            return redirect(url_for('tournaments.index'))

    return render_template('tournaments/create_round.html',
        tournament=tournament, round=round, quiz_pool=quiz_pool)



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
