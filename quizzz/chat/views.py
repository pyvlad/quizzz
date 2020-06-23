from flask import g, request, render_template, flash, redirect, url_for, abort

from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.flashing import Flashing

from . import bp
from .models import Message
from .forms import MessageForm, MessageDeleteForm


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


@bp.route('/<int:message_id>/edit', methods=('GET', 'POST'))
def edit(message_id):
    if message_id:
        msg = get_own_message_by_id(message_id)
    else:
        msg = Message()
        msg.user = g.user
        msg.group = g.group

    form = MessageForm(text=msg.text) # request.form is added automatically as 1st arg by flask-wtf
    delete_form = MessageDeleteForm()

    if request.method == 'POST' and form.validate():
        msg.text = form.text.data

        db = get_db_session()
        db.add(msg)
        db.commit()

        return redirect(url_for('chat.index'))

    for error in form.text.errors:
        flash(error, Flashing.ERROR)

    return render_template('chat/edit.html',
        form=form, delete_form=delete_form,
        data={"message_id": msg.id})



@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    msg = get_own_message_by_id(id)

    form = MessageDeleteForm()

    if form.validate():
        db = get_db_session()
        db.delete(msg)
        db.commit()
        flash("Message has been deleted", Flashing.MESSAGE)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('chat.index'))
