from flask import g, abort

from quizzz.auth.models import User
from quizzz.pagination import paginate

from .models import Message


def _query_messages(round_id):
    return g.db.query(Message, User.id, User.name)\
        .join(User, Message.user_id == User.id)\
        .filter(Message.group_id == g.group.id)\
        .filter(Message.round_id == round_id)\
        .order_by(Message.time_created.desc())


def _make_message(msg, user_id, user_name):
    return {
        "id": msg.id,
        "text": msg.text,
        "user_name": user_name,
        "time_created": msg.time_created,
        "time_updated": msg.time_updated,
        "is_own": g.user.id == user_id
    }


def get_recent_chat_messages(limit, round_id=None):
    """Get specified number of recent chat messages without pagination."""
    query = _query_messages(round_id)
    messages = query[:limit]
    return [_make_message(msg, user_id, user_name)
            for msg, user_id, user_name in messages]


def get_paginated_chat_messages(page, per_page, round_id=None):
    """
    Get messages for given chat.
    ``round_id=None`` means common group chat.
    """
    query = _query_messages(round_id)
    pag = paginate(query, page=page, per_page=per_page, error_out=True, count=True)
    return {
        "pagination": {
            "page": pag.page,
            "per_page": pag.per_page,
            "total_items": pag.total,
            "total_pages": pag.pages,
            "has_next": pag.has_next,
            "next_num": pag.next_num,
            "has_prev": pag.has_prev,
            "prev_num": pag.prev_num,
        },
        "messages": [_make_message(msg, user_id, user_name)
                     for msg, user_id, user_name in pag.get_items()]
    }



def get_own_message_by_id(id):
    """
    Helper function.
    Get message by given id.
    """
    msg = g.db.query(Message).filter(Message.id == id).first()
    if msg is None:
        abort(404, "Message doesn't exist.")
    if msg.user_id != g.user.id:
        abort(403, "What do you think you're doing?")

    return msg
