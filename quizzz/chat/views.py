import re

from flask import g, request, render_template, flash, redirect, url_for

from quizzz.db import get_db_session
from quizzz.flashing import Flashing

from . import bp
from .models import Message
from .queries import get_chat_messages, get_own_message_by_id
from .forms import MessageForm, MessageDeleteForm



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

    if request.method == 'POST':
        # browser creates "\r\n" linebreaks which messes up validation
        form.text.data = form.text.data.replace("\r\n", "\n")
        # replace 3+ linebreaks with 2
        form.text.data = re.sub(r"\n\s*\n\s*\n", '\n\n', form.text.data)
        if form.validate():
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
