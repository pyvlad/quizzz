import pytest
from flask import g, session
from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.chat.models import Message

from .data import MESSAGES, USERS


def test_index(client, auth):
    """
    The <index> view should display messages that were added with the test data.
    When logged in as the author, there should be a link to edit a message.
    """
    auth.login_as("bob")
    response = client.get('/groups/1/chat/')
    for msg in MESSAGES:
        # group 1 messages should be displayed:
        if msg["group_id"] == 1:
            assert msg["text"].encode() in response.data
        else:
            assert msg["text"].encode() not in response.data
        # group 1 messages that belong to bob should be editable:
        href = f"/groups/{msg['group_id']}/chat/{msg['id']}/update"
        if msg["group_id"] == 1 and msg["user_id"] == USERS["bob"]["id"]:
            assert f'href="{href}"'.encode() in response.data
        else:
            assert f'href="{href}"'.encode() not in response.data



def test_author_required(app, client, auth):
    """
    Test authorization to update/delete messages:
    a. the user can't modify other user's messages
    b. the user doesn't see edit link
    """
    auth.login_as("alice")
    assert client.post('/groups/1/chat/1/update').status_code == 403
    assert client.post('/groups/1/chat/1/delete').status_code == 403
    assert b'href="/groups/1/chat/1/update"' not in client.get('/chat').data



@pytest.mark.parametrize('path', (
    f'/groups/1/chat/{len(MESSAGES)+1}/update',
    f'/groups/1/chat/{len(MESSAGES)+1}/delete',
))
def test_exists_required(client, auth, path):
    """
    If message with given ID doesn't exists, 404 should be returned.
    """
    auth.login_as("bob")
    assert client.post(path).status_code == 404



def test_create(client, auth, app):
    """
    The <create> view should:
    a. render and return a 200 OK status for a GET request;
    b. insert new message into the database when valid data is sent in a POST request.
    """
    msg_text = "new message from bob"

    auth.login_as("bob")

    response = client.get('/groups/1/chat/create')
    assert response.status_code == 200

    response = client.post('/groups/1/chat/create', data={'text': msg_text})
    assert 'http://localhost/groups/1/chat/' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.text == msg_text).first()
        assert msg is not None



def test_update(client, auth, app):
    """
    The <update> view should:
    a. render and return a 200 OK status for a GET request.
    b. update existing message data in the database when valid data is sent in a POST request.
    """
    msg_text = "updated message"

    auth.login_as("bob")

    response = client.get('/groups/1/chat/1/update')
    assert response.status_code == 200

    response = client.post('/groups/1/chat/1/update', data={'text': msg_text})
    assert 'http://localhost/groups/1/chat/' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.text == msg_text).first()
        assert msg is not None



@pytest.mark.parametrize('path', (
    '/groups/1/chat/create',
    '/groups/1/chat/1/update',
))
def test_create_update_validate(client, auth, path):
    """
    Both <create> and <update> views should show an error message on invalid data.
    """
    auth.login_as("bob")
    response = client.post(path, data={'text': ''})
    assert b"Message must not be empty." in response.data



def test_delete(client, auth, app):
    """
    The <delete> view should redirect to the index URL
    and the message should no longer exist in the database.
    """
    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.id == 1).first()
        assert msg is not None

    auth.login_as("bob")
    response = client.post('/groups/1/chat/1/delete')
    assert response.headers['Location'] == 'http://localhost/groups/1/chat/'

    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.id == 1).first()
        assert msg is None
