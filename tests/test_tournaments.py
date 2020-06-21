import pytest
import sqlalchemy
from flask import g, session

from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.tournaments.models import Tournament, Round, Play, PlayAnswer

from .data import TOURNAMENTS


TOURNAMENT_REQUEST_PAYLOAD = {
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
    auth.logout()
    response = client.get(url)
    assert response.status_code == 401

    # ben is not group member
    auth.login_as("ben")
    response = client.get(url)
    assert response.status_code == 403

    if admin_only:
        auth.login_as("alice")
        response = client.get(url)
        assert response.status_code == 403



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

    # bob is group admin
    auth.login_as("bob")
    response = client.get('/groups/1/tournaments/')
    assert response.status_code == 200
    assert tournament_name in response.data
    assert view_link in response.data
    assert create_link in response.data
    assert update_link in response.data



def test_create_tournament(app, client, auth):
    """
    Test the <edit> tournament view. It should:
    a. be available to group admin only;
    b. insert the new tournament data into the database when valid data is sent in a POST request.
    """
    create_url = '/groups/1/tournaments/0/edit'
    check_permissions(client, auth, create_url, admin_only=True)

    # POST request should redirect to tournament view
    auth.login_as("bob")
    response = client.post(create_url, data=TOURNAMENT_REQUEST_PAYLOAD)
    assert f'http://localhost/groups/1/tournaments/2/' == response.headers['Location']

    # new tournament should be in database now
    with app.app_context():
        db = get_db_session()
        tournament = db.query(Tournament)\
            .filter(Tournament.name == TOURNAMENT_REQUEST_PAYLOAD["tournament_name"])\
            .first()
        assert tournament is not None



def test_create_round(app, client, auth):
    """
    Test the <edit_round> view. It should:
    a. be available to group admin only;
    b. insert the new round data into the database when valid data is sent in a POST request.
    """
    create_url = '/groups/1/tournaments/1/rounds/0/edit'
    check_permissions(client, auth, create_url, admin_only=True)

    # POST request should redirect to tournament view
    auth.login_as("bob")
    response = client.post(create_url, data=ROUND_REQUEST_PAYLOAD)
    assert f'http://localhost/groups/1/tournaments/1/' == response.headers['Location']

    # new round should be in database now
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
    b. group admin should have access to "edit tournament", "add round", "edit round" links;
    c. users should have access to "view_round" links for each round.
    """
    check_permissions(client, auth, '/groups/1/tournaments/1/')

    LINKS = {
        "edit": b'href="/groups/1/tournaments/1/edit"',
        "add_round": b'href="/groups/1/tournaments/1/rounds/0/edit"',
        "view_round": b'href="/groups/1/rounds/1/"',
        "edit_round": b'href="/groups/1/tournaments/1/rounds/1/edit"'
    }
    def check_links(items, response_data):
        for link_name, presence in items:
            if presence:
                assert LINKS[link_name] in response_data
            else:
                assert LINKS[link_name] not in response_data

    # alice is not group admin:
    auth.login_as("alice")
    response = client.get('/groups/1/tournaments/1/')
    assert response.status_code == 200
    check_links([("edit", False), ("add_round", False), ("view_round", False)], response.data)

    # bob is group admin:
    auth.login_as("bob")
    response = client.get('/groups/1/tournaments/1/')
    assert response.status_code == 200
    check_links([("edit", True), ("add_round", True), ("view_round", False)], response.data)

    # tournament rounds should be listed once they're added:
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)
    response = client.get('/groups/1/tournaments/1/')
    check_links([("edit", True), ("add_round", True), ("view_round", True), ("edit_round", True)],
        response.data)



def test_show_round(client, auth):
    """
    Test the 'show_tournament' view:
    """
    # add the round
    auth.login_as("bob")
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    check_permissions(client, auth, '/groups/1/rounds/1/')

    # view should be available now
    auth.login_as("alice")
    response = client.get('/groups/1/rounds/1/')
    assert response.status_code == 200
    assert b"Take Quiz" in response.data
    assert b'action="/groups/1/rounds/1/start"' in response.data
    assert b"Review Quiz" not in response.data
    assert b'href="/groups/1/rounds/1/review"' not in response.data
    assert b"No one has taken this quiz yet." in response.data

    # play the round
    response = client.post('/groups/1/rounds/1/start', data={})
    response = client.post(response.headers['Location'], data={"q1": 4, "q2": 8})

    # view should contain alice's result now
    response = client.get('/groups/1/rounds/1/')
    assert response.status_code == 200
    assert b"Take Quiz" not in response.data
    assert b'action="/groups/1/rounds/1/start"' not in response.data
    assert b"Review Quiz" in response.data
    assert b'href="/groups/1/rounds/1/review"' in response.data
    assert b'<td class="results-table__cell">alice</td>' in response.data
    assert b'<td class="results-table__cell">2</td>' in response.data


def test_start_round(client, auth):

    auth.login_as("bob")

    # can't play non-existent round
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 404

    # add the round
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    # anonymous users shouldn't be able to play
    auth.logout()
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 401

    # non-group members shouldn't be able to play
    auth.login_as("ben")    # ben is not group member
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 403

    # group members should be able to play
    auth.login_as("bob")
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/groups/1/plays/1/"

    # when clicked multiple times, same link should be returned
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/groups/1/plays/1/"

    # another user should get a different link
    auth.login_as("alice")
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/groups/1/plays/2/"



def test_play_round(app, client, auth):
    # add a new round
    auth.login_as("bob")
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    # start bob's play
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302  # play 1

    # start alice's play
    auth.login_as("alice")
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302 # play 2

    # alice shouldn't be able to access bob's play...
    assert client.get("/groups/1/plays/1/").status_code == 403
    assert client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 8}).status_code == 403
    assert client.get("/groups/1/plays/3/").status_code == 403
    # ...neither should anonymouse users...
    auth.logout()
    assert client.get("/groups/1/plays/1/").status_code == 401
    assert client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 8}).status_code == 401
    assert client.get("/groups/1/plays/3/").status_code == 401
    # ...or non-group members
    auth.login_as("ben")
    assert client.get("/groups/1/plays/1/").status_code == 403
    assert client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 8}).status_code == 403
    assert client.get("/groups/1/plays/3/").status_code == 403

    # there should be 2 plays in DB and no submitted plays yet
    with app.app_context():
        db = get_db_session()
        play_submitted = db.query(Play).filter(Play.is_submitted == True).first()
        assert play_submitted is None
        plays_in_progress = db.query(Play).all()
        assert len(plays_in_progress) == 2

    auth.login_as("bob")

    # submitting incomplete form should return error and not submit quiz
    assert client.post("/groups/1/plays/1/", data={"q1": 4}).status_code == 400
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is False
        assert len(play.answers) == 0

    # submitting invalid option ids (including for other questions)
    # should return error and not submit quiz:
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 4}) # would raise 500
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is False
        assert len(play.answers) == 0

    # submit correct form
    request = client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 8})
    assert request.status_code == 302
    assert request.headers["LOCATION"] == "http://localhost/groups/1/rounds/1/review"
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is True
        assert len(play.answers) == 2
        assert play.result == 2
        time_taken = play.get_server_time()

    # further submissions should return an error and not change results
    request = client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 6})
    assert request.status_code == 403
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is True
        assert len(play.answers) == 2
        assert play.result == 2
        assert play.get_server_time() == time_taken



def test_delete_round(app, client, auth):
    """
    Test the 'delete_round' view:
    - it should delete round itself, all plays for that round, and all submitted play answers.
    """
    auth.login_as("bob")
    assert client.post("/groups/1/tournaments/1/rounds/0/edit",
        data=ROUND_REQUEST_PAYLOAD).status_code == 302 # add a new round
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302 # start play
    assert client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 8}).status_code == 302 # submit

    with app.app_context():
        db = get_db_session()
        round = db.query(Round).filter(Round.id == 1).first()
        assert round is not None
        assert len(round.plays) == 1
        assert len(round.plays[0].answers) == 2

    # access denied for non group admins
    auth.logout()
    assert client.post("/groups/1/rounds/1/delete", data={}).status_code == 401
    auth.login_as("ben")
    assert client.post("/groups/1/rounds/1/delete", data={}).status_code == 403
    auth.login_as("alice")
    assert client.post("/groups/1/rounds/1/delete", data={}).status_code == 403
    auth.login_as("bob")
    assert client.post("/groups/1/rounds/1/delete", data={}).status_code == 302

    with app.app_context():
        db = get_db_session()
        round = db.query(Round).filter(Round.id == 1).first()
        assert round is None
        plays = db.query(Play).all()
        assert len(plays) == 0
        answers = db.query(PlayAnswer).all()
        assert len(answers) == 0



def test_delete_tournament(app, client, auth):
    """
    Test the 'delete_tournament' view:
    - it should delete tournament itself, all rounds, plays, and submitted play answers.
    """
    auth.login_as("bob")
    assert client.post("/groups/1/tournaments/1/rounds/0/edit",
        data=ROUND_REQUEST_PAYLOAD).status_code == 302 # add a new round
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302 # start play
    assert client.post("/groups/1/plays/1/", data={"q1": 4, "q2": 8}).status_code == 302 # submit

    with app.app_context():
        db = get_db_session()
        round = db.query(Round).filter(Round.id == 1).first()
        assert round is not None
        assert len(round.plays) == 1
        assert len(round.plays[0].answers) == 2

    # access denied for non group admins
    auth.logout()
    assert client.post("/groups/1/tournaments/1/delete", data={}).status_code == 401
    auth.login_as("ben")
    assert client.post("/groups/1/tournaments/1/delete", data={}).status_code == 403
    auth.login_as("alice")
    assert client.post("/groups/1/tournaments/1/delete", data={}).status_code == 403
    auth.login_as("bob")
    assert client.post("/groups/1/tournaments/1/delete", data={}).status_code == 302

    with app.app_context():
        db = get_db_session()
        tournament = db.query(Tournament).filter(Tournament.id == 1).first()
        assert tournament is None
        rounds = db.query(Round).filter(Round.tournament_id == 1).all()
        assert len(rounds) == 0
        plays = db.query(Play).all()
        assert len(plays) == 0
        answers = db.query(PlayAnswer).all()
        assert len(answers) == 0