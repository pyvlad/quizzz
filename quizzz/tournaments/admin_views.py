import traceback

from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.permissions import USER, check_user_permissions
from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm

from . import bp
from .models import Tournament, Round
from .queries import query_tournament_by_id, query_round_by_id, query_quiz_pool
from .forms import TournamentForm, RoundForm



@bp.route('/tournaments/<int:tournament_id>/edit', methods=('GET', 'POST'))
def edit_tournament(tournament_id):
    """
    Edit group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = (Tournament() if not tournament_id else query_tournament_by_id(tournament_id))

    if request.method == 'POST':
        form = TournamentForm()
        tournament.populate_from_wtform(form)

        try:
            g.db.add(tournament)
            g.db.commit()
        except:
            traceback.print_exc()
            g.db.rollback()
            flash("Tournament could not be created!", Flashing.ERROR)
        else:
            flash("Tournament successfully created/updated.", Flashing.SUCCESS)
            return redirect(url_for('tournaments.index'))

    else:
        form = TournamentForm(
            tournament_name=tournament.name,
            is_active=tournament.is_active
        )

    data = {
        "tournament": {
            "id": tournament.id,
            "name": tournament.name,
            "is_active": tournament.is_active
        }
    }

    delete_form = EmptyForm()

    navbar_items = [
      ("Groups", url_for("groups.index")),
      (g.group.name, url_for("group.show_group_page")),
      ("Tournaments", url_for("tournaments.index")),
      ((data["tournament"]["id"] and "Edit") or "New", "")
    ]

    return render_template('tournaments/edit.html', form=form, delete_form=delete_form,
        data=data, navbar_items=navbar_items)



@bp.route('/tournaments/<int:tournament_id>/delete', methods=('POST',))
def delete_tournament(tournament_id):
    """
    Delete group tournament.
    """
    check_user_permissions(USER.IS_GROUP_ADMIN)

    form = EmptyForm()

    if form.validate():
        tournament = query_tournament_by_id(tournament_id)
        g.db.delete(tournament)
        g.db.commit()
        flash("Tournament has been deleted.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('tournaments.index'))




@bp.route("/tournaments/<int:tournament_id>/rounds/<int:round_id>/edit", methods=("GET", "POST"))
def edit_round(tournament_id, round_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    tournament = query_tournament_by_id(tournament_id)
    quiz_pool = query_quiz_pool(g.group_id)
    round = Round() if not round_id else query_round_by_id(round_id)

    choices = [
        (quiz.id, "%s by %s" % (quiz.topic, author_name))
        for quiz, author_id, author_name in quiz_pool
    ]
    if round.quiz:
        choices.insert(0, (round.quiz.id, "%s by %s" % (round.quiz.topic, round.quiz.author.name)))


    if request.method == 'POST':
        form = RoundForm()
        form.quiz_id.choices = choices

        if form.validate():
            round.populate_from_wtform(form, tournament_id)

            try:
                g.db.add(round)
                g.db.commit()
            except:
                traceback.print_exc()
                g.db.rollback()
                flash("Quiz Round could not be updated!", Flashing.ERROR)
            else:
                flash("Quiz Round has been created/updated.", Flashing.SUCCESS)
                return redirect(url_for('tournaments.show_tournament_page', tournament_id=tournament_id))
        else:
            flash("Invalid form submitted.")
    else:
        form = RoundForm(
            quiz_id=round.quiz.id if round.quiz else None,
            start_date=round.start_time,
            start_time_hours=round.start_time.hour if round.start_time else 0,
            start_time_minutes=round.start_time.minute if round.start_time else 0,
            finish_date=round.finish_time,
            finish_time_hours=round.finish_time.hour if round.start_time else 0,
            finish_time_minutes=round.finish_time.minute if round.start_time else 0,
        )
        form.quiz_id.choices = choices

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

    delete_form = EmptyForm()

    navbar_items = [
      ("Groups", url_for("groups.index")),
      (g.group.name, url_for("group.show_group_page")),
      ("Tournaments", url_for("tournaments.index")),
      (data["tournament"]["name"], url_for("tournaments.show_tournament_page", tournament_id=data["tournament"]["id"])),
      ("Edit Round" if round_id else "New Round", "")
    ]

    return render_template('tournaments/edit_round.html', form=form, delete_form=delete_form,
        data=data, navbar_items=navbar_items)



@bp.route('/rounds/<int:round_id>/delete', methods=('POST',))
def delete_round(round_id):
    check_user_permissions(USER.IS_GROUP_ADMIN)

    form = EmptyForm()

    if form.validate():
        round = query_round_by_id(round_id)
        g.db.delete(round)
        g.db.commit()
        flash("Quiz round has been deleted.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('tournaments.index'))
