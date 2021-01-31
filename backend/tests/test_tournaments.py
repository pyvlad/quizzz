import pytest
import sqlalchemy
from flask import g, session

from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.tournaments.models import Tournament, Round, Play, PlayAnswer
from quizzz.quizzes.models import Quiz

from .data import TOURNAMENTS, GROUPS, USERS
from .request_data import NOW, LATER, QUIZ_REQUEST_PAYLOAD, TOURNAMENT_REQUEST_PAYLOAD, \
    ROUND_REQUEST_PAYLOAD, VALID_PLAY_DATA


def _finalize_first_quiz(app):
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.id == 1).first()
        quiz.is_finalized = True
        db.commit()


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
    view_link = b'/groups/1/tournaments/1/'
    create_link = b'/groups/1/tournaments/0/edit'
    update_link = b'/groups/1/tournaments/1/edit'

    # alice is not group admin:
    auth.login_as("alice")
    response = client.get('/groups/1/tournaments/')
    assert response.status_code == 200
    assert tournament_name in response.data
    assert view_link in response.data
    assert create_link not in response.data
    assert update_link in response.data # it is in <script> data

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
    assert response.headers['Location'].startswith(f'http://localhost/groups/1/tournaments/')

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

    _finalize_first_quiz(app)

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



def test_show_tournament_page(app, client, auth):
    """
    Test the 'show_tournament_page' view:
    a. it should be available to authenticated group members;
    b. group admin should have access to "edit tournament", "add round", "edit round" links;
    c. users should have access to "view_round" links for each round.
    """
    check_permissions(client, auth, '/groups/1/tournaments/1/')

    LINKS = {
        "add_round": b'/groups/1/tournaments/1/rounds/0/edit',
        "view_round": b'/groups/1/rounds/1/',
        "edit_round": b'/groups/1/tournaments/1/rounds/1/edit'
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
    check_links([("add_round", False), ("view_round", False)], response.data)

    # bob is group admin:
    auth.login_as("bob")
    response = client.get('/groups/1/tournaments/1/')
    assert response.status_code == 200
    check_links([("add_round", True), ("view_round", False)], response.data)

    # tournament rounds should be listed once they're added:
    _finalize_first_quiz(app)
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)
    response = client.get('/groups/1/tournaments/1/')
    check_links([("add_round", True), ("view_round", True), ("edit_round", True)],
        response.data)



def test_show_round_page(app, client, auth):
    """
    Test the 'show_round_page' view.
    """
    # add the round
    auth.login_as("bob")
    _finalize_first_quiz(app)
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
    response = client.post(response.headers['Location'], data=VALID_PLAY_DATA)

    # view should contain alice's result now
    response = client.get('/groups/1/rounds/1/')
    assert response.status_code == 200
    assert b"Take Quiz" not in response.data
    assert b'action="/groups/1/rounds/1/start"' not in response.data
    assert b"Review Quiz" in response.data
    assert b'href="/groups/1/rounds/1/review"' in response.data
    assert b'<td class="table__td">alice</td>' in response.data
    assert b'<td class="table__td table__td--centered">2</td>' in response.data



def test_start_round(app, client, auth):
    """
    Test the 'start_round' view:
    a. it should be available to authenticated group members;
    b. when clicked multiple times, same play should be used.
    """
    auth.login_as("bob")

    # can't play non-existent round
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 404

    # add the round
    _finalize_first_quiz(app)
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    # anonymous users shouldn't be able to play
    auth.logout()
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 401

    # non-group members shouldn't be able to play
    auth.login_as("ben")    # ben is not group member
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 403

    # quiz author should not be able to play
    auth.login_as("bob")
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 403

    # group members should be able to play
    auth.login_as("alice")
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/groups/1/rounds/1/play"
    with app.app_context():
        db = get_db_session()
        play = db.query(Play)\
            .filter(Play.user_id == USERS["alice"]["id"])\
            .filter(Play.round_id == 1)\
            .first()
        assert play.is_submitted is False
        assert len(play.answers) == 0
        assert play.result is None
        time_started = play.server_started
        play_id = play.id

    # when clicked multiple times, same play should be used
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/groups/1/rounds/1/play"
    with app.app_context():
        db = get_db_session()
        play2 = db.query(Play)\
            .filter(Play.user_id == USERS["alice"]["id"])\
            .filter(Play.round_id == 1)\
            .first()
        assert play2.id == play_id
        assert play.server_started == time_started

    # another user should be able to start his play as well
    auth.login_as("ben")
    client.post('/groups/join', data={
            "group_name": GROUPS["group1"]["name"],
            "password": GROUPS["group1"]["password"]
        })
    response = client.post("/groups/1/rounds/1/start", data={})
    assert response.status_code == 302
    assert response.headers['Location'] == "http://localhost/groups/1/rounds/1/play"
    with app.app_context():
        db = get_db_session()
        play3 = db.query(Play)\
            .filter(Play.user_id == USERS["ben"]["id"])\
            .filter(Play.round_id == 1)\
            .first()
        assert play3.id != play_id



def test_play_round(app, client, auth):
    """
    Test the 'play_round' view:
    a. it should be available to authenticated group members who clicked 'start round';
    b. correct form submission should create Play.answers collection,
       toggle Play.is_submitted, calculate result, and stop the timer.
    c. user can only play round once.
    """
    # add a new round
    auth.login_as("bob")
    _finalize_first_quiz(app)
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    # anonymous users shouldn't be able to play...
    auth.logout()
    assert client.get("/groups/1/rounds/1/play").status_code == 401
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 401

    # ...neither should non-group members...
    auth.login_as("ben")
    assert client.get("/groups/1/rounds/1/play").status_code == 403
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 403

    # ...non-started play is unavailable as well...
    auth.login_as("bob")
    assert client.get("/groups/1/rounds/1/play").status_code == 403
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 403
    auth.login_as("alice")
    assert client.get("/groups/1/rounds/1/play").status_code == 403
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 403

    # start alice's play
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302 # play 1

    # there should be 1 play in DB at this point and no submitted plays yet
    with app.app_context():
        db = get_db_session()
        play_submitted = db.query(Play).filter(Play.is_submitted == True).first()
        assert play_submitted is None
        plays_in_progress = db.query(Play).all()
        assert len(plays_in_progress) == 1

    # submit correct form
    response = client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA)
    assert response.status_code == 302
    assert response.headers["LOCATION"] == "http://localhost/groups/1/rounds/1/review"
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is True
        assert len(play.answers) == 2
        assert play.result == 2
        time_taken = play.get_server_time()

    # further attempts to play should return an error
    assert client.get("/groups/1/rounds/1/play").status_code == 403

    # further submissions should return an error and not change results
    valid_play_data = VALID_PLAY_DATA.copy()
    valid_play_data["questions-1-answer"] = "6"
    request = client.post("/groups/1/rounds/1/play", data=valid_play_data)
    assert request.status_code == 403
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is True
        assert len(play.answers) == 2
        assert play.result == 2
        assert play.get_server_time() == time_taken



def test_play_round_errors(app, client, auth):
    """
    Test that a submitted form deviating from the expected form
    is invalidated as expected.
    """
    # add a new round
    auth.login_as("bob")
    _finalize_first_quiz(app)
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    # start alice's play
    auth.login_as("alice")
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302  # play 1

    def assert_play_not_in_db():
        with app.app_context():
            db = get_db_session()
            play = db.query(Play).filter(Play.id == 1).first()
            assert play.is_submitted is False
            assert len(play.answers) == 0

    # submitting invalid forms
    # (a) missing question_id
    invalid_play_data = VALID_PLAY_DATA.copy()
    del invalid_play_data["questions-0-question_id"]
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 400
    assert_play_not_in_db()

    # (b) missing question (entirely)
    invalid_play_data = VALID_PLAY_DATA.copy()
    del invalid_play_data["questions-1-question_id"]
    del invalid_play_data["questions-1-answer"]
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 400
    assert_play_not_in_db()

    # (c) invalid option id (including for other questions)
    invalid_play_data = VALID_PLAY_DATA.copy()
    invalid_play_data["questions-1-answer"] = invalid_play_data["questions-0-answer"]
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 400
    assert_play_not_in_db()

    # (d) same added twice replacing another question
    invalid_play_data = VALID_PLAY_DATA.copy()
    invalid_play_data["questions-1-question_id"] = invalid_play_data["questions-0-question_id"]
    invalid_play_data["questions-1-answer"] = invalid_play_data["questions-0-answer"]
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 400
    assert_play_not_in_db()

    # (e) bad value
    invalid_play_data = VALID_PLAY_DATA.copy()
    invalid_play_data["questions-1-question_id"] = ""
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 400
    assert_play_not_in_db()

    # (f) question from another quiz
    # add another quiz and query first question
    auth.login_as("bob")
    response = client.post('/groups/1/quizzes/0/edit', data=QUIZ_REQUEST_PAYLOAD)
    with app.app_context():
        db = get_db_session()
        quiz2 = db.query(Quiz).filter(Quiz.id == 2).first()
        question_id = quiz2.questions[0].id
        correct_option_id = [opt for opt in quiz2.questions[0].options if opt.is_correct][0].id
    # plugging that question into another quiz triggers an error
    auth.login_as("alice")
    invalid_play_data = VALID_PLAY_DATA.copy()
    invalid_play_data["questions-1-question_id"] = str(question_id)
    invalid_play_data["questions-1-answer"] = str(correct_option_id)
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 400
    assert_play_not_in_db()

    # (g) extra repeats are stripped off
    # correct submission happens
    invalid_play_data = VALID_PLAY_DATA.copy()
    invalid_play_data["questions-2-question_id"] = invalid_play_data["questions-0-question_id"]
    invalid_play_data["questions-2-answer"] = invalid_play_data["questions-0-answer"]
    response = client.post("/groups/1/rounds/1/play", data=invalid_play_data)
    assert response.status_code == 302
    assert response.headers["LOCATION"] == "http://localhost/groups/1/rounds/1/review"
    with app.app_context():
        db = get_db_session()
        play = db.query(Play).filter(Play.id == 1).first()
        assert play.is_submitted is True
        assert len(play.answers) == 2
        assert play.result == 2

    # example with expected sqlalchemy error:
    # with pytest.raises(sqlalchemy.exc.IntegrityError):
    #     client.post("/groups/1/rounds/1/play", data={"questions-0-answer": "4", "questions-1-answer": "4"}) # would raise 500



def test_review_round(app, client, auth):
    """ """
    # add a new round
    auth.login_as("bob")
    _finalize_first_quiz(app)
    client.post("/groups/1/tournaments/1/rounds/0/edit", data=ROUND_REQUEST_PAYLOAD)

    # cannot review round if anonymous
    auth.logout()
    assert client.get("/groups/1/rounds/1/review").status_code == 401

    # cannot review round of not group member
    auth.login_as("ben")
    assert client.get("/groups/1/rounds/1/review").status_code == 403

    # can review if quiz author
    auth.login_as("bob")
    assert client.get("/groups/1/rounds/1/review").status_code == 200

    # cannot review round if not started a play yet
    auth.login_as("alice")
    assert client.get("/groups/1/rounds/1/review").status_code == 403

    # start alice's play
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302

    # cannot review round of not submitted a play yet
    assert client.get("/groups/1/rounds/1/review").status_code == 403

    # submit alice's play
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 302

    # can review now
    assert client.get("/groups/1/rounds/1/review").status_code == 200

    # other group members who have not played yet still cannot review round
    auth.login_as("ben")
    client.post('/groups/join', data={
            "group_name": GROUPS["group1"]["name"],
            "password": GROUPS["group1"]["password"]
        })
    assert client.get("/groups/1/rounds/1/review").status_code == 403



def test_delete_round(app, client, auth):
    """
    Test the 'delete_round' view:
    - it should delete round itself, all plays for that round, and all submitted play answers.
    """
    auth.login_as("bob")
    _finalize_first_quiz(app)
    assert client.post("/groups/1/tournaments/1/rounds/0/edit",
        data=ROUND_REQUEST_PAYLOAD).status_code == 302 # add a new round
    auth.login_as("alice")
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302 # start play
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 302 # submit

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



def test_inactive_round(app, client, auth):
    """
    Test the round's time_started and time_finished behaviour:
    - a round cannot be played outside of (time_started, time_finished) time span;
    -
    """
    auth.login_as("bob")
    _finalize_first_quiz(app)

    # a. add a new round that already finished and try playing it
    payload = ROUND_REQUEST_PAYLOAD.copy()
    payload.update({
        "finish_date": NOW.strftime("%Y-%m-%d"),
        "finish_time_hours": NOW.hour,
        "finish_time_minutes": NOW.minute,
    })
    assert client.post("/groups/1/tournaments/1/rounds/0/edit", data=payload).status_code == 302
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 403

    # delete the round to re-use quiz_id=1
    assert client.post("/groups/1/rounds/1/delete", data={}).status_code == 302
    # b. add a new round that has not started yet and try playing it
    payload = ROUND_REQUEST_PAYLOAD.copy()
    payload.update({
        "start_date": LATER.strftime("%Y-%m-%d"),
        "start_time_hours": LATER.hour,
        "start_time_minutes": LATER.minute,
    })
    assert client.post("/groups/1/tournaments/1/rounds/0/edit", data=payload).status_code == 302
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 403



def test_delete_tournament(app, client, auth):
    """
    Test the 'delete_tournament' view:
    - it should delete tournament itself, all rounds, plays, and submitted play answers.
    """
    auth.login_as("bob")
    _finalize_first_quiz(app)
    assert client.post("/groups/1/tournaments/1/rounds/0/edit",
        data=ROUND_REQUEST_PAYLOAD).status_code == 302 # add a new round
    auth.login_as("alice")
    assert client.post("/groups/1/rounds/1/start", data={}).status_code == 302 # start play
    assert client.post("/groups/1/rounds/1/play", data=VALID_PLAY_DATA).status_code == 302 # submit

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
