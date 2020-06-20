import traceback

from sqlalchemy.orm import joinedload
from flask import current_app, render_template, g, flash, request, redirect, url_for, abort

from quizzz.db import get_db_session
from quizzz.flashing import Flashing

from . import bp
from .models import Quiz, Question, Option



# *** HELPERS ***
def get_own_quiz_by_id(quiz_id, with_questions=False):
    db = get_db_session()

    if with_questions:
        quiz = db.query(Quiz)\
            .options(joinedload(Quiz.questions).joinedload(Question.options))\
            .filter(Quiz.id == quiz_id)\
            .first()
    else:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if quiz is None:
        abort(404, "Quiz doesn't exist.")
    if quiz.author_id != g.user.id:
        abort(403, "What do you think you're doing?")

    return quiz



# *** VIEWS ***
@bp.route('/')
def index():
    """
    Get list of quizzes of logged in user in current group.
    """
    db = get_db_session()

    user_quizzes_in_progress = db.query(Quiz)\
        .filter(Quiz.author_id == g.user.id)\
        .filter(Quiz.group_id == g.group.id)\
        .filter(Quiz.is_finalized != True)\
        .order_by(Quiz.time_created.desc())\
        .all()

    user_quizzes_finalized = db.query(Quiz)\
        .filter(Quiz.author_id == g.user.id)\
        .filter(Quiz.group_id == g.group.id)\
        .filter(Quiz.is_finalized == True)\
        .order_by(Quiz.time_created.desc())\
        .all()

    data = {
        "user_quizzes_in_progress": user_quizzes_in_progress,
        "user_quizzes_finalized": user_quizzes_finalized
    }

    return render_template('quizzes/index.html', data=data)



@bp.route('/<int:quiz_id>/edit', methods=('GET', 'POST'))
def edit(quiz_id):
    if quiz_id:
        quiz = get_own_quiz_by_id(quiz_id, with_questions=True)
    else:
        quiz = Quiz()
        quiz.init_questions()


    if request.method == 'POST':
        if quiz.is_finalized:
            abort(403, "Cannot update submitted quiz.")

        quiz.populate_from_request_form(request.form)

        db = get_db_session()
        try:
            db.add(quiz)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz could not be saved!", Flashing.ERROR)
        else:
            if quiz.is_finalized:
                flash("Submitted!", Flashing.SUCCESS)
                return redirect(url_for('quizzes.index'))
            else:
                flash("Saved!", Flashing.MESSAGE)
                return redirect(url_for('quizzes.edit', quiz_id=quiz.id))

    num_questions = current_app.config["QUESTIONS_PER_QUIZ"]
    num_options = current_app.config["OPTIONS_PER_QUESTION"]
    form_fields = [
        ("topic", quiz.topic),
        ("is_finalized", quiz.is_finalized),
        *[(f"question_{qnum+1}", quiz.questions[qnum].text)
            for qnum in range(num_questions)],
        *[(f"question_{qnum+1}_answer", str(optnum + 1))
            for qnum in range(num_questions) for optnum in range(num_options)
            if quiz.questions[qnum].options[optnum].is_correct],
        *[(f"question_{qnum+1}_option_{optnum+1}", quiz.questions[qnum].options[optnum].text)
            for qnum in range(num_questions) for optnum in range(num_options)]
    ]

    data = {
        "quiz_id": quiz.id,
        "read_only": quiz.is_finalized,
        "num_questions": num_questions,
        "num_options": num_options,
        "quiz": ({k: request.form.get(k, default) for k, default in form_fields}
            if request.form
            else dict(form_fields)
        )
    }

    return render_template('quizzes/edit.html', data=data)



@bp.route('/<int:quiz_id>/delete', methods=('POST',))
def delete(quiz_id):
    quiz = get_own_quiz_by_id(quiz_id)

    if quiz.is_finalized:
        abort(403, "Can not delete submitted quiz.")

    db = get_db_session()
    db.delete(quiz)
    db.commit()

    return redirect(url_for('quizzes.index'))
