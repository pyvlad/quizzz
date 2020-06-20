import traceback

from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.permissions import USER, check_user_permissions
from quizzz.db import get_db_session
from quizzz.flashing import Flashing

from . import bp
from .models import Tournament, Round
from .queries import get_tournament_by_id, get_quiz_pool, get_round_by_id



@bp.route('/tournaments/<int:tournament_id>/edit', methods=('GET', 'POST'))
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
            flash("Tournament could not be created!", Flashing.ERROR)
        else:
            flash("Tournament successfully created/updated.", Flashing.SUCCESS)
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



@bp.route('/tournaments/<int:tournament_id>/delete', methods=('POST',))
def delete_tournament(tournament_id):
    """
    Delete group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = get_tournament_by_id(tournament_id)

    db = get_db_session()
    db.delete(tournament)
    db.commit()
    flash("Tournament has been deleted.", Flashing.SUCCESS)

    return redirect(url_for('tournaments.index'))




@bp.route("/tournaments/<int:tournament_id>/rounds/<int:round_id>/edit", methods=("GET", "POST"))
def edit_round(tournament_id, round_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = get_tournament_by_id(tournament_id)
    quiz_pool = get_quiz_pool(g.group_id)
    round = Round() if not round_id else get_round_by_id(round_id)

    if request.method == 'POST':
        round.populate_from_request_form(request.form, tournament_id)

        db = get_db_session()
        try:
            db.add(round)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz Round could not be updated!", Flashing.ERROR)
        else:
            flash("Quiz Round has been created/updated.", Flashing.SUCCESS)
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
    round = get_round_by_id(round_id)
    db.delete(round)
    db.commit()
    flash("Quiz round has been deleted.", Flashing.SUCCESS)

    return redirect(url_for('tournaments.index'))
