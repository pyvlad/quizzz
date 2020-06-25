from flask import g, abort

from quizzz.db import get_db_session
from quizzz.auth.models import User

from .models import Message


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
