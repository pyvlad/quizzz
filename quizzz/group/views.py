from flask import g, render_template

from . import bp
from quizzz.quizzes.queries import get_user_group_quizzes
from quizzz.chat.queries import get_chat_messages


@bp.route('/')
def show_group_page():
    group_tournaments = g.group.tournaments
    current_tournaments = [
        { "id": tournament.id, "name": tournament.name }
        for tournament in group_tournaments if tournament.is_active
    ]

    num_user_quizzes_in_progress = get_user_group_quizzes(which="in-progress", return_count=True)
    num_user_quizzes_finalized = get_user_group_quizzes(which="finalized", return_count=True)

    chat_messages = get_chat_messages(limit=5)

    data = {
        "group": {
            "id": g.group.id,
            "name": g.group.name
        },
        "current_tournaments": current_tournaments,
        "num_user_quizzes_in_progress": num_user_quizzes_in_progress,
        "num_user_quizzes_finalized": num_user_quizzes_finalized,
        "chat_messages": chat_messages
    }

    return render_template('group/group_page.html', data=data)
