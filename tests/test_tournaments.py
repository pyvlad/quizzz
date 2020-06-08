import pytest
from flask import g, session

from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.tournaments.models import Tournament, Round

from .data import TOURNAMENTS


REQUEST_PAYLOAD = {
    "tournament_name": "Tournament 2",
    "has_started": True,
    "has_finished": False
}

ROUND_REQUEST_PAYLOAD = {
    "quiz_id": 1,
    "start_time": "2020-10-10",
    "finish_time": "2021-10-10"
}


def check_permissions(client, auth, url, admin_only=False):
    response = client.get(url)
    assert response.status_code == 401

    # ben is not group member
    auth.login_as("ben")
    response = client.get(url)
    assert response.status_code == 403
    auth.logout()

    if admin_only:
        auth.login_as("alice")
        response = client.get(url)
        assert response.status_code == 403
        auth.logout()




def test_index(client, auth):
    """
    Test the <index> view:
    a. it should display a list of group tournaments to authenticated group members;
    b. there should be a link to view each tournament;
    c. there should be links to add and edit tournaments if the user is group admin.
    """
    check_permissions(client, auth, '/groups/1/tournaments/')

    tournament_name = TOURNAMENTS["tournament1"]["name"].encode()
    view_link = b'href="/groups/1/tournaments/1/"'
    create_link = b'href="/groups/1/tournaments/0/edit"'
    update_link = b'href="/groups/1/tournaments/1/edit"'

    # alice is not group admin:
    auth.login_as("alice")
    response = client.get('/groups/1/tournaments/')
    assert response.status_code == 200
    assert tournament_name in response.data
    assert view_link in response.data
    assert create_link not in response.data
    assert update_link not in response.data
    auth.logout()

    # bob is group admin
    auth.login_as("bob")
    response = client.get('/groups/1/tournaments/')
    assert response.status_code == 200
    assert tournament_name in response.data
    assert view_link in response.data
    assert create_link in response.data
    assert update_link in response.data



def test_edit_tournament(app, client, auth):
    """
    Test the <edit> tournament view. It should:
    a. be available to group admin only;
    b. insert the new tournament data into the database when valid data is sent in a POST request.
    """
    create_url = '/groups/1/tournaments/0/edit'
    check_permissions(client, auth, create_url, admin_only=True)

    # POST request should redirect to tournament view
    auth.login_as("bob")
    response = client.post(create_url, data=REQUEST_PAYLOAD)
    assert f'http://localhost/groups/1/tournaments/2/' == response.headers['Location']

    # new tournament should be in database now
    with app.app_context():
        db = get_db_session()
        tournament = db.query(Tournament)\
            .filter(Tournament.name == REQUEST_PAYLOAD["tournament_name"])\
            .first()
        assert tournament is not None



def test_edit_round(app, client, auth):
    """
    Test the <edit_round> view. It should:
    a. be available to group admin only;
    b. insert the new tournament data into the database when valid data is sent in a POST request.
    """
    create_url = '/groups/1/tournaments/1/rounds/0/edit'
    check_permissions(client, auth, create_url, admin_only=True)

    # POST request should rdirect to tournament view
    auth.login_as("bob")
    response = client.post(create_url, data=ROUND_REQUEST_PAYLOAD)
    assert f'http://localhost/groups/1/tournaments/1/' == response.headers['Location']

    # new tournament should be in database now
    with app.app_context():
        db = get_db_session()
        round = db.query(Round)\
            .filter(Round.quiz_id == ROUND_REQUEST_PAYLOAD["quiz_id"])\
            .first()
        assert round is not None



def test_show_tournament(client, auth):
    """
    Test the 'show_tournament' view:
    a. it should be available to authenticated group members;
    b. group admin should have access to "edit tournament", "add round", "edit_round" links;
    c.
    """
    check_permissions(client, auth, '/groups/1/tournaments/1/')

    edit_link = b'href="/groups/1/tournaments/1/edit"'
    add_round_link = b'href="/groups/1/tournaments/1/rounds/0/edit"'
    round_link = b'href="/groups/1/tournaments/rounds/1/"'

    # alice is not group admin:
    auth.login_as("alice")
    response = client.get('/groups/1/tournaments/1/')
    assert response.status_code == 200
    assert edit_link not in response.data
    assert add_round_link not in response.data
    auth.logout()

    # bob is group admin:
    auth.login_as("bob")
    response = client.get('/groups/1/tournaments/1/')
    assert response.status_code == 200
    assert edit_link in response.data
    assert add_round_link in response.data

    # tournament rounds should be listed once they're added
    assert round_link not in response.data
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)
    response = client.get('/groups/1/tournaments/1/')
    assert round_link in response.data
