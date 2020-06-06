import traceback
from flask import current_app, render_template, g, flash, request, redirect, url_for, abort
from . import bp
from .models import Play, PlayAnswer
from quizzz.quizzes.models import Quiz
from quizzz.db import get_db_session


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



@bp.route('/<int:quiz_id>/play', methods=('GET', 'POST'))
def take_quiz(quiz_id):
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if g.group.id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    db = get_db_session()
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        abort(404, "Quiz doesn't exist.")

    play = db.query(Play).filter(Play.quiz_id == quiz.id).filter(Play.user_id == g.user.id).first()
    if play is None:
        play = Play(user=g.user, quiz=quiz)
        db.add(play)
        db.commit()

    if play.is_submitted:
        abort(400, "You already took this quiz before.")

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


    if request.method == 'POST':
        # TODO: what if submission fails (e.g. incomplete form)?
        answers = []
        for q in quiz.questions:
            submitted_option_id = request.form["q%s" % q.id]

            options = [opt for opt in q.options if str(opt.id) == submitted_option_id]
            if not len(options):
                abort(400, "Option ID mismatch.")
            option = options[0]

            answers += [PlayAnswer(play=play, option=option)]

        play.is_submitted = True
        play.result = len([answer for answer in answers if answer.option.is_correct])
        db.add(play)
        db.commit()

        return redirect(url_for("plays.review_quiz", quiz_id=quiz_id))

    return render_template('plays/take_quiz.html', data=data)



@bp.route('/<int:quiz_id>/review', methods=('GET',))
def review_quiz(quiz_id):
    if not g.user:
        abort(403, "You're not logged in.")

    user_group_ids = { m.group_id for m in g.user.memberships }
    if g.group.id not in user_group_ids:
        abort(403, "You're not a member of this group.")

    db = get_db_session()
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        abort(404, "Quiz doesn't exist.")

    play = db.query(Play)\
        .filter(Play.quiz_id == quiz_id)\
        .filter(Play.user_id == g.user.id)\
        .first()
    if not play or not play.is_submitted:
        abort(400, "You can't review a quiz before you take it!")

    data = {
        "quiz_topic": quiz.topic,
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
            for qnum, question in enumerate(quiz.questions)
        ]
    }

    return render_template('plays/review_quiz.html', data=data)
