import traceback

from flask import g, flash, request, redirect, url_for, abort, render_template
from . import bp
from .models import Tournament
from .user_permissions import USER, check_user_permissions
from quizzz.db import get_db_session



@bp.route('/')
def index():
    """
    Get list of group tournaments.
    """
    check_user_permissions(USER.IS_GROUP_MEMBER)

    group_memberships = list(g.group.members)
    group_member_user_ids = [m.user_id for m in group_memberships]
    membership = group_memberships[group_member_user_ids.index(g.user.id)]

    data = {
        "tournaments": [
            {
                "id": tournament.id,
                "name": tournament.name
            }
            for tournament in g.group.tournaments
        ],
        "has_edit_permissions": membership.is_admin
    }

    return render_template('tournaments/tournament_list.html', data=data)



@bp.route('/<int:tournament_id>/')
def show_tournament(tournament_id):
    """
    Show tournament details.
    """
    check_user_permissions(USER.IS_GROUP_MEMBER)

    db = get_db_session()
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        abort(404, "This tournament doesn't exist.")

    group_memberships = list(g.group.members)
    group_member_user_ids = [m.user_id for m in group_memberships]
    membership = group_memberships[group_member_user_ids.index(g.user.id)]

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
        "has_edit_permissions": membership.is_admin
    }
    
    return render_template('tournaments/tournament.html', data=data)



@bp.route("/create", methods=('GET', 'POST'))
def create_tournament():
    """
    Create new group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = None

    if request.method == 'POST':
        tournament = Tournament()
        tournament.name = request.form["tournament_name"]
        tournament.has_started = bool(request.form.get("has_started"))
        tournament.has_finished = bool(request.form.get("has_finished"))
        tournament.group = g.group

        db = get_db_session()
        try:
            db.add(tournament)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Tournament could not be created!")
        else:
            flash("Tournament has been created.")
            return redirect(url_for('tournaments.index'))

    return render_template('tournaments/create_tournament.html', tournament=tournament)



@bp.route('/<int:tournament_id>/update', methods=('GET', 'POST'))
def update_tournament(tournament_id):
    """
    Create new group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    db = get_db_session()
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        abort(400, "Tournament doesn't exist.")

    if request.method == 'POST':
        tournament.name = request.form["tournament_name"]
        tournament.has_started = bool(request.form.get("has_started"))
        tournament.has_finished = bool(request.form.get("has_finished"))

        try:
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Tournament could not be created!")
        else:
            flash("Tournament has been updated.")
            return redirect(url_for('tournaments.index'))

    return render_template('tournaments/create_tournament.html', tournament=tournament)



@bp.route('/<int:tournament_id>/delete', methods=('POST',))
def delete_tournament(tournament_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    db = get_db_session()
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament:
        db.delete(tournament)
        flash("Tournament has been deleted.")
    else:
        abort(400, "Tournament doesn't exist.")
    db.commit()

    return redirect(url_for('tournaments.index'))
