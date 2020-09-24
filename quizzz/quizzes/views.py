import traceback

from flask import current_app, render_template, g, flash, request, redirect, url_for, abort

from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm
from quizzz.momentjs import momentjs

from . import bp
from .models import Quiz
from .queries import query_quiz_by_id, query_user_quizzes
from .forms import make_quiz_form



@bp.route('/')
def index():
    """
    Get list of quizzes of logged in user in current group.
    """
    user_quizzes = query_user_quizzes(
        user_id=g.user.id,
        group_id=g.group.id
    )

    data = {
        "user_quizzes": [
            {
                "id": quiz.id,
                "topic": quiz.topic,
                "is_submitted": quiz.is_finalized,
                "last_update": (
                    momentjs(quiz.time_updated)._timestamp_as_iso_8601()
                    if quiz.time_updated
                    else momentjs(quiz.time_created)._timestamp_as_iso_8601()
                ),
                "edit_url": url_for('quizzes.edit', quiz_id=quiz.id)
            } for quiz in user_quizzes
        ]
    }

    navbar_items = [
      ("Groups", url_for("groups.index")),
      (g.group.name, url_for("group.show_group_page")),
      ("Your Quizzes", url_for("quizzes.index"))
    ]

    return render_template('quizzes/index.html', data=data, navbar_items=navbar_items)



@bp.route('/<int:quiz_id>/edit', methods=('GET', 'POST'))
def edit(quiz_id):
    # 1. load/initialize quiz object with questions
    if quiz_id:
        quiz = query_quiz_by_id(quiz_id, with_questions=True)
        if quiz.author_id != g.user.id:
            abort(403, "This is not your quiz!")
        if quiz.group_id != g.group.id:
            abort(403, "This quiz belongs to another group!")
    else:
        quiz = Quiz()
        quiz.author = g.user
        quiz.group = g.group
        quiz.num_questions = current_app.config["QUESTIONS_PER_QUIZ"]
        quiz.num_options = current_app.config["OPTIONS_PER_QUESTION"]
        quiz.init_questions()

    # 2. handle form submission
    if request.method == 'POST':

        # 2a. already submitted quiz cannot be modified
        if quiz.is_finalized:
            abort(403, "Cannot update submitted quiz.")

        # 2b. identify which button was clicked
        is_being_submitted = request.form.get("finalize_me", False)

        # 2c. create appropriate form class based on quiz configuration and user action
        QuizForm = make_quiz_form(quiz.num_questions, quiz.num_options, finalize=is_being_submitted)

        # 2d. initialize form (implicitly loads data from request.POST)
        form = QuizForm()

        # 2e. if data is valid, populate ORM object from form data and save
        if form.validate():
            # 2f. populate quiz object from wtform
            quiz.topic = form.topic.data
            quiz.is_finalized = True if is_being_submitted else False
            for qnum, question in enumerate(quiz.questions):
                question_subform = form.questions[qnum].form
                question.text = question_subform.text.data
                for optnum, option in enumerate(question.options):
                    option.text = question_subform.options[optnum].form.text.data
                    option.is_correct = (question_subform.answer.data == str(optnum))

            # 2g. save
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
                    flash("Saved!", Flashing.SUCCESS)
                    return redirect(url_for('quizzes.edit', quiz_id=quiz.id))
        else:
            flash("Bad quiz was submitted. Please correct the errors below and save/submit again.",
                Flashing.ERROR)
            # proceed to re-render form with appropriate validation: submit/save

    # 3. handle GET request
    else:
        # 3a. create appropriate form class based on quiz configuration
        QuizForm = make_quiz_form(quiz.num_questions, quiz.num_options, finalize=False)

        # 3b. populate form from loaded/initialized ORM objects
        form = QuizForm(
            topic=quiz.topic,
            questions=[
                {
                    "text": question.text,
                    "options": [
                        {
                            "text": opt.text
                        } for opt in question.options
                    ],
                    "answer": {
                        opt.is_correct: str(num)
                        for num, opt in enumerate(question.options)
                    }.get(True, "")
                } for question in quiz.questions
            ]
        )

    # 4. some extra params to render template correctly
    data = {
        "quiz_id": quiz.id,
        "read_only": quiz.is_finalized,
    }

    delete_form = EmptyForm()

    navbar_items = [
      ("Groups", url_for("groups.index")),
      (g.group.name, url_for("group.show_group_page")),
      ("My Quizzes", url_for("quizzes.index")),
      ((data["quiz_id"] and "Edit") or "New", "")
    ]

    return render_template(
        'quizzes/edit.html',
        form=form,
        delete_form=delete_form,
        data=data,
        navbar_items=navbar_items
    )



@bp.route('/<int:quiz_id>/delete', methods=('POST',))
def delete(quiz_id):
    form = EmptyForm()

    if form.validate():
        quiz = query_quiz_by_id(quiz_id)
        if quiz.author_id != g.user.id:
            abort(403, "What do you think you're doing?")
        if quiz.is_finalized:
            abort(403, "Can not delete submitted quiz.")

        g.db.delete(quiz)
        g.db.commit()
        flash("Quiz has been deleted.", Flashing.SUCCESS)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('quizzes.index'))
