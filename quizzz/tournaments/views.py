from sqlalchemy.orm import joinedload
from flask import g, flash, request, redirect, url_for, abort, render_template

from quizzz.momentjs import momentjs

from . import bp
from .models import Play
from .queries import query_tournament_by_id, query_round_by_id, query_play
from .preps import (
    prep_tournament,
    prep_round,
    prep_round_list,
    prep_tournament_standings,
    prep_round_standings
)
from .forms import make_play_round_form


TOURNAMENT_FILTERS = ["active", "inactive", "all"]
ROUND_FILTERS = ["current", "finished", "coming", "all"]


# --- list of tournaments ---
@bp.route('/tournaments/')
def index():
    """
    Get list of group tournaments.
    """
    filter_arg = request.args.get("filter", "active")
    if filter_arg not in TOURNAMENT_FILTERS:
        abort(400)

    tournament_list = g.group.tournaments

    data = {
        "tournaments": [prep_tournament(t) for t in tournament_list],
        "is_admin": g.group_membership.is_admin,
        "filters": [(filtr, (filter_arg == filtr)) for filtr in TOURNAMENT_FILTERS]
    }

    return render_template('tournaments/index.html', data=data)


# --- single tournament / list of rounds / cumulative list of plays (tournament standings) ---
@bp.route('/tournaments/<int:tournament_id>/')
def show_tournament_page(tournament_id):
    """
    Show tournament information:
    - list of rounds,
    - overall standings.
    """
    filter_arg = request.args.get("filter", "current")
    if filter_arg not in ROUND_FILTERS:
        abort(400)

    # TODO: maybe 2 queries instead?
    tournament = query_tournament_by_id(tournament_id, with_rounds=True, with_plays=True)

    data = {
        "tournament": prep_tournament(tournament),
        "rounds": prep_round_list(tournament, user_id=g.user.id),
        "tournament_standings": prep_tournament_standings(tournament),
        "is_admin": g.group_membership.is_admin,
        "filters": [(filtr, (filter_arg == filtr)) for filtr in ROUND_FILTERS]
    }

    return render_template('tournaments/tournament.html', data=data)


# --- single round / list of plays (round standings) ---
@bp.route('/rounds/<int:round_id>/')
def show_round_page(round_id):
    """
    Show round information:
    - tournament, quiz, and round descriptions,
    - round standings (sorted list of plays).
    """
    round = query_round_by_id(round_id, with_tournament=True, with_author=True, with_plays=True)

    data = {
        "tournament": prep_tournament(round.tournament),
        "round": prep_round(round, g.user.id),
        "round_standings": prep_round_standings(round.plays)
    }

    return render_template('tournaments/round.html', data=data)


# --- start a play ---
@bp.route('/rounds/<int:round_id>/start', methods=('POST',))
def start_round(round_id):
    """
    Start a round performing necessary checks:
    - if user is logged in & is group member & round is active,
      create new <play> object with initialized <start_time>, otherwise abort;
    - if user already started this round, use previously created play object;
    - if user already finished this round, abort.
    Given a valid <play> object, redirect to the play view.
    When round is no longer active, no play can be started or re-loaded.
    """
    round = query_round_by_id(round_id)
    if not round.is_active:
        abort(403, "This round is not available (already finished or not started yet).")

    play = query_play(round_id, g.user.id, abort_if_none=False)
    if play and play.is_submitted:
        abort(403, "You have already played this round.")

    if play is None:
        play = Play(user=g.user, round=round)
        g.db.add(play)
        g.db.commit()

    return redirect(url_for("tournaments.play_round", round_id=round_id))


# --- take a quiz (fill in and submit quiz form / finalize play) ---
@bp.route('/rounds/<int:round_id>/play', methods=('GET', 'POST'))
def play_round(round_id):
    """
    Take the round's quiz.
    """
    # 1a. load the play, ensure it was initialized but not submitted:
    play = query_play(round_id, user_id=g.user.id, abort_if_none=False)
    if not play:
        abort(403, "You need to start the round first.")
    if play.is_submitted:
        abort(403, "You have already played this round.")

    # 1b. load quiz with questions
    round = query_round_by_id(round_id, with_questions=True)

    # 2. create quiz form and fill it with data
    # 2a. dynamically create form class
    PlayRoundForm = make_play_round_form(len(round.quiz.questions))
    # 2b. initialize the form and (if it's a POST request) populate with data from <request.form>:
    form = PlayRoundForm()
    # 2c. dynamically add form.answer.choices with (<option_id>, <option_text>) as (value, label)
    for qnum, question in enumerate(round.quiz.questions):
        choices = []
        for optnum, option in enumerate(question.options):
            choices += [(str(option.id), option.text)]
        form.questions[qnum].form.answer.choices = choices
    # 2d. add hidden question_id for GET requests
    if request.method == 'GET':
        for qnum, question in enumerate(round.quiz.questions):
            form.questions[qnum].form.question_id.data = str(question.id)

    # 3. handle form submission
    if request.method == 'POST':
        # won't validate if number of questions is different from expected
        if form.validate():
            # (a) add <play.answers>
            # (b) toggle <play.is_submitted>
            # (c) calculate <play.result>
            play.populate_from_wtform(form) # wrong question_id will lead to abort here
            g.db.commit()
            return redirect(url_for("tournaments.review_round", round_id=round_id))
        else:
            abort(400, "Invalid form submitted.")

    # 4. prepare more data to render in GET requests
    data = {
        "quiz_topic": round.quiz.topic,
        "questions": {str(q.id): q.text for q in round.quiz.questions}
    }

    return render_template('tournaments/play_round.html', form=form, data=data)


# --- review quiz with selected and correct answers ---
@bp.route('/rounds/<int:round_id>/review', methods=('GET',))
def review_round(round_id):
    """
    Review the round's quiz.
    """
    # (a) load round with questions and user's play with options selected
    round = query_round_by_id(round_id, with_questions=True, with_tournament=True)
    play = query_play(round_id, g.user.id, with_answers=True, abort_if_none=False)

    # (b) ensure the user cannot review correct answers before he submits his quiz
    if not play or not play.is_submitted:
        abort(403, "You can't review a quiz before you take it!")

    # (c) prepare dict with selected options by question_id
    answers_by_question_id = { pa.question_id: pa.option for pa in play.answers }
    selected_options = {}
    for question in round.quiz.questions:
        option = answers_by_question_id.get(question.id)
        question_dict = {}
        question_dict["option_id"] = option.id if option else None
        question_dict["is_correct"] = option.is_correct if option else False
        selected_options[question.id] = question_dict

    # (d) prepare data for rendering
    data = {
        "tournament": prep_tournament(round.tournament),
        "round": {
            "id": round.id,
            "quiz": {
                "topic": round.quiz.topic,
            }
        },
        "questions": [
            {
                "id": question.id,
                "text": question.text,
                "comment": question.comment,
                "is_answer_correct": selected_options.get(question.id)["is_correct"],
                "options": [
                    {
                        "id": option.id,
                        "text": option.text,
                        "is_correct": option.is_correct,
                        "is_selected": option.id == selected_options.get(question.id)["option_id"],
                    }
                    for option in question.options
                ]
            }
            for question in round.quiz.questions
        ]
    }

    return render_template('tournaments/review_round.html', data=data)
