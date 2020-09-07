from flask import g, render_template, current_app, url_for

from . import bp
from quizzz.quizzes.queries import get_user_group_quizzes
from quizzz.chat.queries import get_paginated_chat_messages



@bp.route('/')
def show_group_page():
    num_current_tournaments = len([t for t in g.group.tournaments if t.is_active])
    num_user_quizzes_in_progress = get_user_group_quizzes(which="in-progress", return_count=True)
    num_user_quizzes_finalized = get_user_group_quizzes(which="finalized", return_count=True)
    chat_data = get_paginated_chat_messages(
        1, current_app.config["CHAT_MESSAGES_PER_PAGE"], round_id=None)
    num_members = len(g.group.members)

    data = {
        "group": {
            "id": g.group.id,
            "name": g.group.name
        },
        "num_current_tournaments": num_current_tournaments,
        "num_user_quizzes_in_progress": num_user_quizzes_in_progress,
        "num_user_quizzes_finalized": num_user_quizzes_finalized,
        "num_chat_messages": chat_data["pagination"]["total_items"],
        "last_message": (chat_data["messages"][0]
            if chat_data["messages"] else None),
        "num_members": num_members
    }

    navbar_items = [
      ("Groups", url_for("groups.index")),
      (data["group"]["name"], ""),
    ]

    return render_template('group/group_page.html', data=data, navbar_items=navbar_items)
