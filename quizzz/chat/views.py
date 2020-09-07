import re

from flask import escape, current_app, g, request, render_template, flash, redirect, \
    url_for, jsonify, abort

from quizzz.flashing import Flashing
from quizzz.forms import EmptyForm
from quizzz.momentjs import momentjs

from . import bp
from .models import Message
from .queries import get_paginated_chat_messages, get_own_message_by_id
from .forms import MessageForm

from quizzz.tournaments.queries import query_round_by_id, query_play


def _retrieve_round_id_and_run_checks():
    try:
        round_id = request.args.get("round_id", None)
        if round_id is not None:
            round_id = int(round_id)
    except (TypeError, ValueError):
        abort(400)

    if round_id:
        # (a) load round and user's play
        round = query_round_by_id(round_id, with_author=True)
        play = query_play(round_id, g.user.id, abort_if_none=False)

        # (b) ensure the user cannot view chat before he plays the round
        if not round.is_authored_by(g.user.id):
            if not play or not play.is_submitted:
                abort(403, "You can't view this chat before you play the round!")

    return round_id



@bp.route('/')
def index():
    navbar_items = [
      ("Groups", url_for("groups.index")),
      (g.group.name, url_for("group.show_group_page")),
      ("Chat", "")
    ]

    return render_template('chat/index.html', navbar_items=navbar_items)



@bp.route('/api/')
def api_index():
    round_id = _retrieve_round_id_and_run_checks()

    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        abort(400)

    per_page = current_app.config["CHAT_MESSAGES_PER_PAGE"]
    data = get_paginated_chat_messages(page, per_page, round_id=round_id)
    # mutate messages for use in JS:
    for msg in data["messages"]:
        msg["time_created"] = momentjs(msg["time_created"])._timestamp_as_iso_8601()
        msg["time_updated"] = momentjs(msg["time_updated"])._timestamp_as_iso_8601() if msg["time_updated"] else ""
        msg["text"] = escape(msg["text"])

    return jsonify(data)



@bp.route('/<int:message_id>/edit', methods=('GET', 'POST'))
def edit(message_id):
    round_id = _retrieve_round_id_and_run_checks()

    if message_id:
        msg = get_own_message_by_id(message_id)
    else:
        msg = Message(round_id=round_id)
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
            msg_round_id = msg.round_id # save to variable to avoid an extra query after commit
            g.db.commit()

            return (redirect(url_for('tournaments.review_round', round_id=msg_round_id))
                if msg_round_id else redirect(url_for('chat.index')))

    for error in form.text.errors:
        flash(error, Flashing.ERROR)

    data = {
        "message_id": msg.id
    }

    navbar_items = [
      ("Groups", url_for("groups.index")),
      (g.group.name, url_for("group.show_group_page")),
      ("Chat", url_for("chat.index")),
      ("Message", "")
    ]

    return render_template('chat/edit.html', form=form, delete_form=delete_form,
        data=data, navbar_items=navbar_items)



@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    msg = get_own_message_by_id(id)

    msg_round_id = msg.round_id # save to variable to avoid an extra query after commit

    form = EmptyForm()

    if form.validate():
        g.db.delete(msg)
        g.db.commit()
        flash("Message has been deleted", Flashing.MESSAGE)
    else:
        flash("Invalid form submitted.", Flashing.ERROR)

    return (redirect(url_for('tournaments.review_round', round_id=msg_round_id))
        if msg_round_id else redirect(url_for('chat.index')))
