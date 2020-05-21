import pytest
from flask import g, session
from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.chat.models import Message


def test_index(client, auth):
    """
    The index view should display information about the post that was added with the test data.
    When logged in as the author, there should be a link to edit the post.
    Also tests some more authentication behavior while testing the index view.
    """
    response = client.get('/groups/1/chat/')
    assert b"Login" in response.data
    assert b"Register" in response.data

    auth.login(username="bob", password="dog")
    response = client.get('/groups/1/chat/')
    assert b'Log Out' in response.data
    assert b'hello from bob' in response.data
    assert b'hello from alice' in response.data
    assert b'hello again from alice' not in response.data
    assert b'href="/groups/1/chat/1/update"' in response.data
    assert b'href="/groups/1/chat/2/update"' not in response.data



def test_author_required(app, client, auth):
    """
    Test authorization to update/delete messages.
    a. test user can't modify other user's post
    b. test user doesn't see edit link
    """
    auth.login()
    assert client.post('/groups/1/chat/1/update').status_code == 403
    assert client.post('/groups/1/chat/1/delete').status_code == 403
    assert b'href="/groups/1/chat/1/update"' not in client.get('/chat').data



@pytest.mark.parametrize('path', (
    '/groups/1/chat/4/update',
    '/groups/1/chat/4/delete',
))
def test_exists_required(client, auth, path):
    """
    If message with given ID doesn't exists, 404 should be returned.
    """
    auth.login()
    assert client.post(path).status_code == 404



def test_create(client, auth, app):
    """
    The <create> view should:
    a. render and return a 200 OK status for a GET request.
    b. insert the new post data into the database when valid data is sent in a POST request.
    """
    msg_text = "test message 1"

    auth.login()
    assert client.get('/groups/1/chat/create').status_code == 200
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
    msg_text = "test message updated"

    auth.login()
    assert client.get('/groups/1/chat/2/update').status_code == 200
    response = client.post('/groups/1/chat/2/update', data={'text': msg_text})
    assert 'http://localhost/groups/1/chat/' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.text == msg_text).first()
        assert msg is not None



@pytest.mark.parametrize('path', (
    '/groups/1/chat/create',
    '/groups/1/chat/2/update',
))
def test_create_update_validate(client, auth, path):
    """
    Both <create> and <update> views should show an error message on invalid data.
    """
    auth.login()
    response = client.post(path, data={'text': ''})
    assert b'empty message' in response.data



def test_delete(client, auth, app):
    """
    The delete view should redirect to the index URL
    and the post should no longer exist in the database.
    """
    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.id == 2).first()
        assert msg is not None

    auth.login()
    response = client.post('/groups/1/chat/2/delete')
    assert response.headers['Location'] == 'http://localhost/groups/1/chat/'

    with app.app_context():
        db = get_db_session()
        msg = db.query(Message).filter(Message.id == 2).first()
        assert msg is None
