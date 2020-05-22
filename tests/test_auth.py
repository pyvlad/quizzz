import pytest
from flask import g, session
from quizzz.db import get_db_session
from quizzz.auth.models import User


def test_register(client, app):
    """
    a. The register view should render successfully on GET.
    b. On POST with valid form data, it should redirect to the login URL
       and the user’s data should be in the database.
    """
    assert client.get('/auth/register').status_code == 200

    response = client.post('/auth/register', data={'username': 'a', 'password': 'a'})
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        user = db.query(User).filter(User.name == "a").first()
        assert user is not None



@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'username is required'),
    ('a', '', b'password is required'),
    ('bob', 'test', b'already exists'),
))
def test_register_validate_input(client, username, password, message):
    """
    Invalid data should display error messages.
    """
    response = client.post('/auth/register', data={'username': username, 'password': password})
    assert message in response.data




def test_login(client, auth):
    """
    a. The login view should render successfully on GET.
    b. On POST with valid form data, it should redirect to the index URL
       and the user’s id should be in the session.
    """
    assert client.get('/auth/login').status_code == 200

    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 2
        assert g.user.name == 'alice'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'incorrect username'),
    ('alice', 'a', b'incorrect password'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data



def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session



def test_redirect_if_logged_in(client, auth):
    auth.login()

    response = client.get('/auth/login')
    assert response.status_code == 302
    assert 'http://localhost/' == response.headers['Location']

    assert client.post('/auth/login', data={}).status_code == 302

    response = client.get('/auth/register')
    assert response.status_code == 302
    assert 'http://localhost/' == response.headers['Location']

    assert client.post('/auth/register', data={}).status_code == 302
