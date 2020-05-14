import traceback
from flask import current_app, render_template, g, flash, request, redirect, url_for, abort
from . import bp
from .models import Play, PlayAnswer
from quizzz.quiz.models import Quiz
from quizzz.db import get_db_session


@bp.route('/')
def index():
    """ Get list of available and played quizzes of logged in user. """
    db = get_db_session()
    quizzes_available = db.query(Quiz)\
        .filter(Quiz.group_id == g.group.id)\
        .order_by(Quiz.created.desc())\
        .all()
    return render_template('plays/index.html', quizzes_available=quizzes_available)


@bp.route('/<int:quiz_id>/play', methods=('GET', 'POST'))
def take_quiz(quiz_id):
    if g.user is None:
        abort(403, "log in required")

    db = get_db_session()
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        abort(404, "quiz doesn't exist")

    play = db.query(Play).filter(Play.quiz_id == quiz.id).filter(Play.user_id == g.user.id).first()
    if play is None:
        play = Play(user=g.user, quiz=quiz)
        db.add(play)
        db.commit()

    if request.method == 'POST':
        answers = []
        for q in quiz.questions:
            submitted_option_id = request.form["q%s" % q.id]
            options = [opt for opt in q.options if str(opt.id) == submitted_option_id]
            if not len(options):
                abort(400, "Option ID mismatch.")
            option = options[0]
            answers += [PlayAnswer(play=play, option=option)]

        play.result = len([answer for answer in answers if answer.option.is_correct])
        db.add(play)
        db.commit()

        return render_template('plays/review_quiz.html',
            quiz=quiz, play=play, enumerate=enumerate, zip=zip)

    return render_template('plays/take_quiz.html', quiz=quiz, enumerate=enumerate)
