from flask import render_template, flash, request, g, redirect, url_for, abort
from . import bp
from .models import Message
from quizzz.db import get_db_session


@bp.route('/')
def index():
    db = get_db_session()
    messages = db.query(Message).order_by(Message.created.desc()).all()
    return render_template('chat/index.html', messages=messages)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        text = request.form['text']

        error = None
        if not text:
            error = 'empty message'

        if error is not None:
            flash(error)
        else:
            db = get_db_session()
            msg = Message(text=text, user=g.user)
            db.add(msg)
            db.commit()
            return redirect(url_for('chat.index'))

    return render_template('chat/create.html')



def get_message_by_id(id, check_author=True):
    db = get_db_session()

    msg = db.query(Message).filter(Message.id == id).first()
    if msg is None:
        abort(404, "message doesn't exist")
    if check_author and msg.user_id != g.user.id:
        abort(403, "what do you think you're doing?")

    return msg



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    msg = get_message_by_id(id)

    if request.method == 'POST':
        text = request.form['text']

        error = None
        if not text:
            error = 'empty message'

        if error is not None:
            flash(error)
        else:
            db = get_db_session()
            msg.text = text
            db.add(msg)
            db.commit()
            return redirect(url_for('chat.index'))

    return render_template('chat/update.html', msg=msg)



@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    msg = get_message_by_id(id)
    db = get_db_session()
    db.delete(msg)
    db.commit()
    return redirect(url_for('chat.index'))