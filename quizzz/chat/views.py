import re

from flask import current_app, g, request, render_template, flash, redirect, url_for

from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm

from . import bp
from .models import Message
from .queries import get_paginated_chat_messages, get_own_message_by_id
from .forms import MessageForm



@bp.route('/')
def index():
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        abort(404)
    per_page = current_app.config["CHAT_MESSAGES_PER_PAGE"]
    data = get_paginated_chat_messages(page, per_page, round_id=None)

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
    delete_form = EmptyForm()

    if request.method == 'POST':
        # browser creates "\r\n" linebreaks which messes up validation
        form.text.data = form.text.data.replace("\r\n", "\n")
        # replace 3+ linebreaks with 2
        form.text.data = re.sub(r"\n\s*\n\s*\n", '\n\n', form.text.data)
        if form.validate():
            msg.text = form.text.data

            g.db.add(msg)
            g.db.commit()

            return redirect(url_for('chat.index'))

    for error in form.text.errors:
        flash(error, Flashing.ERROR)

    return render_template('chat/edit.html',
        form=form, delete_form=delete_form,
        data={"message_id": msg.id})



@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    msg = get_own_message_by_id(id)

    form = EmptyForm()

    if form.validate():
        g.db.delete(msg)
        g.db.commit()
        flash("Message has been deleted", Flashing.MESSAGE)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return redirect(url_for('chat.index'))
