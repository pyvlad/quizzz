import pytest

from flask import g, session

from quizzz.db import get_db_session
from quizzz.auth.models import User

from .data import USERS



def test_base_template(client, auth):
    """
    Test that menu updates according to login status.
    """
    response = client.get('/')
    assert b"Login" in response.data
    assert b"Register" in response.data
    assert b"Log Out" not in response.data

    auth.login_as("bob")
    response = client.get('/', follow_redirects=True)
    assert b"Login" not in response.data
    assert b"Register" not in response.data
    assert b'Log Out' in response.data



def test_register(client, app):
    """
    a. The register view should render successfully on GET.
    b. On POST with valid form data:
        b1. it should redirect to the login URL
        b2. the user’s data should be in the database.
    """
    assert client.get('/auth/register').status_code == 200

    response = client.post('/auth/register', data={'username': 'new_user', 'password': 'new_pass'})
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        user = db.query(User).filter(User.name == "new_user").first()
        assert user is not None



@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username cannot be shorter'),
    ('a', '', b'Password cannot be shorter'),
    (USERS["bob"]["name"], 'some_pass', f'User {USERS["bob"]["name"]} already exists.'.encode()),
    (USERS["bob"]["name"].upper(), 'some_pass', f'User {USERS["bob"]["name"]} already exists.'.encode()),
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
    b. On POST with valid form data:
        b1. it should redirect to the index URL;
        b2. the user’s id should be in the session.
    """
    assert client.get('/auth/login').status_code == 200

    response = auth.login_as("bob")
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == g.user.uuid
        assert g.user.name == USERS["bob"]["name"]

    auth.logout()

    # log in user even if username was entered in different case
    response = auth.login(USERS["alice"]["name"].upper(), USERS["alice"]["password"])
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == g.user.uuid
        assert g.user.name == USERS["alice"]["name"]



@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    (USERS["alice"]["name"], 'wrong password', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """
    Invalid credentials should display error messages.
    """
    response = auth.login(username, password)
    assert message in response.data



def test_logout(client, auth):
    """
    After logout, user_id should be removed from the session.
    """
    auth.login_as("bob")

    with client:
        auth.logout()
        assert 'user_id' not in session



def test_redirect_if_logged_in(client, auth):
    """
    The views 'register' and 'login' should redirect to home page
    for logged in users.
    """
    auth.login(USERS["bob"]["name"], USERS["bob"]["password"])

    response = client.get('/auth/login')
    assert response.status_code == 302
    assert 'http://localhost/' == response.headers['Location']

    assert client.post('/auth/login', data={}).status_code == 302

    response = client.get('/auth/register')
    assert response.status_code == 302
    assert 'http://localhost/' == response.headers['Location']

    assert client.post('/auth/register', data={}).status_code == 302
