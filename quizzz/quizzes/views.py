import traceback

from flask import current_app, render_template, g, flash, request, redirect, url_for, abort

from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm

from . import bp
from .models import Quiz
from .queries import get_own_quiz_by_id, get_user_group_quizzes
from .forms import make_quiz_form



@bp.route('/')
def index():
    """
    Get list of quizzes of logged in user in current group.
    """
    user_quizzes_in_progress = get_user_group_quizzes(which="in-progress")
    user_quizzes_finalized = get_user_group_quizzes(which="finalized")

    data = {
        "user_quizzes_in_progress": user_quizzes_in_progress,
        "user_quizzes_finalized": user_quizzes_finalized
    }

    return render_template('quizzes/index.html', data=data)



@bp.route('/<int:quiz_id>/edit', methods=('GET', 'POST'))
def edit(quiz_id):
    # load or initialize quiz object with questions
    if quiz_id:
        quiz = get_own_quiz_by_id(quiz_id, with_questions=True)
    else:
        quiz = Quiz()
        quiz.is_finalized = False
        quiz.num_questions = current_app.config["QUESTIONS_PER_QUIZ"]
        quiz.num_options = current_app.config["OPTIONS_PER_QUESTION"]
        quiz.init_questions()

    # create appropriate form class based on quiz configuration
    QuizForm = make_quiz_form(quiz.num_questions, quiz.num_options)

    if request.method == 'POST':
        # bail out of updating if submitted
        if quiz.is_finalized:
            abort(403, "Cannot update submitted quiz.")

        # otherwise initialize form (implicitly loads data from request.POST)
        form = QuizForm()

        # if data is valid, populate ORM object from form data and save
        if form.validate():
            quiz.populate_from_wtform(form)

            try:
                g.db.add(quiz)
                g.db.commit()
            except:
                traceback.print_exc()
                g.db.rollback()
                flash("Quiz could not be saved!", Flashing.ERROR)
            else:
                if quiz.is_finalized:
                    flash("Submitted!", Flashing.SUCCESS)
                    return redirect(url_for('quizzes.index'))
                else:
                    flash("Saved!", Flashing.MESSAGE)
                    return redirect(url_for('quizzes.edit', quiz_id=quiz.id))
        else:
            flash("Bad form was submitted!")

    # if this is GET request, populate form from loaded/initialized ORM objects
    else:
        form = QuizForm(
            topic=quiz.topic,
            is_finalized="1" if quiz.is_finalized else "0",
            questions=[
                {
                    "text": question.text,
                    "options": [
                        {"text": opt.text} for opt in question.options
                    ],
                    "answer": {
                        opt.is_correct: str(num)
                        for num, opt in enumerate(question.options)
                    }.get(True, "")
                } for question in quiz.questions
            ]
        )

    # some extra params to render template correctly
    data = {
        "quiz_id": quiz.id,
        "read_only": quiz.is_finalized,
    }

    delete_form = EmptyForm()

    return render_template('quizzes/edit.html', form=form, delete_form=delete_form, data=data)



@bp.route('/<int:quiz_id>/delete', methods=('POST',))
def delete(quiz_id):
    form = EmptyForm()

    if form.validate():
        quiz = get_own_quiz_by_id(quiz_id)
        if quiz.is_finalized:
            abort(403, "Can not delete submitted quiz.")

        g.db.delete(quiz)
        g.db.commit()
        flash("Quiz has been deleted.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('quizzes.index'))
