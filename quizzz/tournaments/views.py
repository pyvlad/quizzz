from sqlalchemy.orm import joinedload
from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.db import get_db_session

from . import bp
from .models import Play
from .queries import (
    get_tournament_by_id,
    get_tournament_standings,
    get_round_by_id,
    get_round_with_quiz_by_id,
    get_round_with_details_by_id,
    get_quiz_pool,
    get_play_by_round_id,
    get_played_rounds_by_tournament_id
)
from .forms import make_play_round_form


@bp.route('/tournaments/')
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



@bp.route('/tournaments/<int:tournament_id>/')
def show_tournament(tournament_id):
    """
    Show tournament details.
    """
    tournament = get_tournament_by_id(tournament_id, with_rounds=True)
    standings = get_tournament_standings(tournament_id)
    played_round_ids = get_played_rounds_by_tournament_id(tournament_id)

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
                    "is_taken": round.id in played_round_ids
                }
                for round in tournament.rounds
            ]
        },
        "standings": standings,
        "has_edit_permissions": g.group_membership.is_admin
    }

    return render_template('tournaments/tournament.html', data=data)





@bp.route('/rounds/<int:round_id>/')
def show_round(round_id):
    """
    Show round details.
    """
    round = get_round_with_details_by_id(round_id)
    users_played = set(play.user.id for play in round.plays)

    round_plays = sorted([
        {
            "id": play.id,
            "user": play.user.name,
            "user_id": play.user.id,
            "result": play.result,
            "time": play.get_server_time(),
            "score": play.get_score()
        }
        for play in round.plays
    ], key=lambda x: x["score"], reverse=True)

    data = {
        "tournament": {
            "id": round.tournament.id,
            "name": round.tournament.name
        },
        "quiz": {
            "id": round.quiz.id,
            "topic": round.quiz.topic,
            "author": round.quiz.author.name,
            "plays": round_plays
        },
        "round": {
            "id": round.id,
        },
        "is_taken": g.user.id in users_played
    }

    return render_template('tournaments/round.html', data=data)



@bp.route('/rounds/<int:round_id>/start', methods=('POST',))
def start_round(round_id):
    db = get_db_session()

    round = get_round_by_id(round_id)
    play = get_play_by_round_id(round_id)

    if play is None:
        play = Play(user=g.user, round=round)
        db.add(play)
        db.commit()

    if play.is_submitted:
        abort(403, "You have already played this round.")

    return redirect(url_for("tournaments.play_round", play_id=play.id))



@bp.route('/plays/<int:play_id>/', methods=('GET', 'POST'))
def play_round(play_id):
    """
    Take the round's quiz.
    """
    db = get_db_session()

    play = db.query(Play).filter(Play.id == play_id).first()
    if not play or play.user_id != g.user.id:
        abort(403)
    if play.is_submitted:
        abort(403, "You have already played this round.")

    round = get_round_with_quiz_by_id(play.round_id)
    round_id = play.round_id
    quiz = round.quiz

    # create form, dynamically add choices
    PlayRoundForm = make_play_round_form(len(quiz.questions))
    form = PlayRoundForm()  # add choices from request form if it's POST
    for qnum, question in enumerate(quiz.questions):
        form.questions[qnum].form.answer.choices = [
            (str(option.id), 'abcdefghij'[optnum])
            for optnum, option in enumerate(question.options)
        ]

    if request.method == 'POST':
        if form.validate():
            play.populate_from_wtform(form)
            db.commit()
            return redirect(url_for("tournaments.review_round", round_id=round_id))
        else:
            flash("Invalid form submitted.")

    data = {
        "quiz_topic": quiz.topic,
        "questions": [
            {
                "number": qnum,
                "id": question.id,
                "text": question.text,
                "options": [
                    {
                        "number": optnum,
                        "id": option.id,
                        "text": option.text
                    }
                    for optnum, option in enumerate(question.options)
                ]
            }
            for qnum, question in enumerate(quiz.questions, 1)
        ]
    }

    return render_template('tournaments/play_round.html', form=form, data=data)




@bp.route('/rounds/<int:round_id>/review', methods=('GET',))
def review_round(round_id):
    """
    Review the round's quiz.
    """
    round = get_round_with_quiz_by_id(round_id)
    play = get_play_by_round_id(round_id, with_answers=True)
    tournament = get_tournament_by_id(round.tournament_id)

    if not play or not play.is_submitted:
        abort(403, "You can't review a quiz before you take it!")

    data = {
        "quiz_topic": round.quiz.topic,
        "questions": [
            {
                "number": qnum + 1,
                "id": question.id,
                "text": question.text,
                "options": [
                    {
                        "number": optnum,
                        "id": option.id,
                        "text": option.text,
                        "is_correct": option.is_correct
                    }
                    for optnum, option in enumerate(question.options)
                ],
                "answer": {
                    "option_id": play.answers[qnum].option.id,
                    "is_correct": play.answers[qnum].option.is_correct
                },
                "comment": question.comment
            }
            for qnum, question in enumerate(round.quiz.questions)
        ],
        "tournament": {
            "id": tournament.id,
            "name": tournament.name
        },
        "round": {
            "id": round.id
        }
    }

    return render_template('tournaments/review_round.html', data=data)
