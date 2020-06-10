import traceback

from flask import current_app, render_template, g, flash, request, redirect, url_for, abort

from quizzz.quizzes.models import Quiz
from quizzz.db import get_db_session

from . import bp
from .models import Play, PlayAnswer


@bp.route('/')
def index():
    """
    Get list of available and played quizzes of logged in user.
    """
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if g.group.id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    db = get_db_session()

    group_quizzes = db.query(Quiz)\
        .filter(Quiz.group_id == g.group.id)\
        .filter(Quiz.author_id != g.user.id)\
        .order_by(Quiz.time_created.desc())\
        .all()
    played_quizzes = [p for p in g.user.plays if p.is_submitted]
    played_quiz_ids = {p.quiz_id for p in played_quizzes}
    available_quizzes = [q for q in group_quizzes if q.id not in played_quiz_ids]

    data = {
        "played_quizzes": [
            {
                "id": play.quiz.id,
                "topic": play.quiz.topic,
                "author": play.quiz.author.name,
                "tournament": play.quiz.round.tournament.name if play.quiz.round else "",
                "date": str(play.server_started.date()) + " " + str(play.server_started.time())[:5],
                "result": play.result,
                "time": play.get_server_time()
            }
            for play in played_quizzes
        ],
        "available_quizzes": [
            {
                "id": quiz.id,
                "topic": quiz.topic,
                "author": quiz.author.name
            }
            for quiz in available_quizzes
        ]
    }

    return render_template('plays/index.html', data=data)
