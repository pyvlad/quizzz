from flask import g, request, render_template, flash, redirect, url_for, abort

from quizzz.db import get_db_session
from quizzz.auth.models import User

from . import bp
from .models import Message


# *** HELPERS ***
def get_chat_messages(round_id=None):
    """
    Helper function.
    Get messages for given chat.
    "round_id=None" means common group chat.
    """
    db = get_db_session()
    messages = db.query(Message, User.id, User.name)\
        .join(User, Message.user_id == User.id)\
        .filter(Message.group_id == g.group.id)\
        .filter(Message.round_id == round_id)\
        .order_by(Message.time_created.desc())\
        .all()

    return [
        {
            "id": msg.id,
            "text": msg.text,
            "user_name": user_name,
            "time_created": msg.time_created,
            "time_updated": msg.time_updated,
            "is_own": g.user.id == user_id
        }
        for msg, user_id, user_name in messages
    ]



def get_own_message_by_id(id):
    """
    Helper function.
    Get message by given id.
    """
    db = get_db_session()

    msg = db.query(Message).filter(Message.id == id).first()
    if msg is None:
        abort(404, "Message doesn't exist.")
    if msg.user_id != g.user.id:
        abort(403, "What do you think you're doing?")

    return msg



# *** VIEWS ****
@bp.route('/')
def index():
    data = {
        "messages": get_chat_messages()
    }
    return render_template('chat/index.html', data=data)



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

    return render_template('chat/edit.html', data={})



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    msg = get_own_message_by_id(id)

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

    return render_template('chat/edit.html', data={"msg": msg})



@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    msg = get_own_message_by_id(id)
    db = get_db_session()
    db.delete(msg)
    db.commit()
    return redirect(url_for('chat.index'))
