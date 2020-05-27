from flask import g, request, render_template, flash, redirect, url_for, abort
from . import bp
from .models import Message
from quizzz.db import get_db_session


@bp.route('/')
def index():
    db = get_db_session()
    messages = db.query(Message)\
        .filter(Message.group == g.group)\
        .order_by(Message.created.desc())\
        .all()
    return render_template('chat/index.html', messages=messages)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        text = request.form['text']

        error = None
        if not text:
            error = "Message must not be empty."

        if error is not None:
            flash(error)
        else:
            db = get_db_session()
            msg = Message(text=text, user=g.user, group=g.group)
            db.add(msg)
            db.commit()
            return redirect(url_for('chat.index'))

    return render_template('chat/edit.html')



def get_message_by_id(id, check_author=True):
    db = get_db_session()

    msg = db.query(Message).filter(Message.id == id).first()
    if msg is None:
        abort(404, "Message doesn't exist.")
    if check_author and msg.user_id != g.user.id:
        abort(403, "What do you think you're doing?")

    return msg



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    msg = get_message_by_id(id)

    if request.method == 'POST':
        text = request.form['text']

        error = None
        if not text:
            error = "Message must not be empty."

        if error is not None:
            flash(error)
        else:
            db = get_db_session()
            msg.text = text
            db.add(msg)
            db.commit()
            return redirect(url_for('chat.index'))

    return render_template('chat/edit.html', msg=msg)



@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    msg = get_message_by_id(id)
    db = get_db_session()
    db.delete(msg)
    db.commit()
    return redirect(url_for('chat.index'))
