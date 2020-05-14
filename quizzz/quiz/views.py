import traceback
from flask import current_app, render_template, g, flash, request, redirect, url_for, abort
from . import bp
from .models import Quiz, Question, Option
from quizzz.db import get_db_session


@bp.route('/')
def index():
    """ Get list of quizzes of logged in user. """
    db = get_db_session()
    if not g.user or not g.group:
        abort(400)
    your_quizzes = db.query(Quiz)\
        .filter(Quiz.author_id == g.user.id)\
        .filter(Quiz.group_id == g.group.id)\
        .order_by(Quiz.created.desc())\
        .all()
    return render_template('quiz/index.html', your_quizzes=your_quizzes)



@bp.route('/create', methods=('GET', 'POST'))
def create():
    quiz = None

    if request.method == 'POST':
        if not g.user:
            abort(403)
        if not g.group:
            abort(400)
        quiz = Quiz.from_request_form(request.form)

        db = get_db_session()
        try:
            db.add(quiz)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz could not be saved!")
        else:
            if quiz.is_finalized:
                flash("Submitted!")
                return redirect(url_for('quiz.index'))
            else:
                flash("Saved!")
                return redirect(url_for('quiz.update', quiz_id=quiz.id))

    return render_template('quiz/create.html', quiz=quiz)



def get_quiz_by_id(quiz_id, check_author=True):
    db = get_db_session()

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        abort(404, "quiz doesn't exist")
    if not g.user:
        abort(403, "need to be logged in!")
    if check_author and quiz.author_id != g.user.id:
        abort(403, "what do you think you're doing?")

    return quiz



@bp.route('/<int:quiz_id>/update', methods=('GET', 'POST'))
def update(quiz_id):
    quiz = get_quiz_by_id(quiz_id)

    if request.method == 'POST':
        new_quiz = Quiz.from_request_form(request.form)

        db = get_db_session()
        try:
            db.delete(quiz)
            db.add(new_quiz)
            db.commit()
        except:
            traceback.print_exc()
            db.rollback()
            flash("Quiz could not be saved!")
        else:
            if new_quiz.is_finalized:
                flash("Submitted!")
                return redirect(url_for('quiz.index'))
            else:
                flash("Updated!")
                return redirect(url_for('quiz.update', quiz_id=new_quiz.id))

    return render_template('quiz/create.html', quiz=quiz)



@bp.route('/<int:quiz_id>/delete', methods=('POST',))
def delete(quiz_id):
    quiz = get_quiz_by_id(quiz_id)
    db = get_db_session()
    db.delete(quiz)
    db.commit()
    return redirect(url_for('quiz.index'))
