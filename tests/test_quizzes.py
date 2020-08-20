import pytest
from flask import g, session
from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.quizzes.models import Quiz, Question, Option

from .data import USERS, QUIZZES, QUIZ_QUESTIONS, QUESTION_OPTIONS


REQUEST_PAYLOAD = {
    "topic": "Quiz 2",
    "is_finalized": "0",
    "questions-0-text": "What is love?",
    "questions-0-answer": "3",
    "questions-0-options-0-text": "baby, don't hurt me",
    "questions-0-options-1-text": "don't hurt me",
    "questions-0-options-2-text": "no more",
    "questions-0-options-3-text": "all of these",
    "questions-1-text": "How much is the fish?",
    "questions-1-answer": "3",
    "questions-1-options-0-text": "lala-lalala-la-la",
    "questions-1-options-1-text": "lalalala",
    "questions-1-options-2-text": "lala-lalala-la-lalala",
    "questions-1-options-3-text": "all of these"
}


def test_models(app):
    """
    Test whether conftest objects have been inserted as expected:
    a. Quiz has been inserted;
    b. Number of questions is as expected;
    c. Number of correct answers equals to the number of questions.
    """
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).first()
        assert quiz is not None
        assert len(quiz.questions) == len(QUIZ_QUESTIONS)
        assert len([opt for q in quiz.questions for opt in q.options if opt.is_correct]) == len(QUIZ_QUESTIONS)



def test_index(client, auth):
    """
    Test the <index> view:
    a. it should display quizzes added by logged in user;
    b. there should be a link to edit/view the quiz.
    """
    response = client.get('/groups/2/quizzes/')
    assert response.status_code == 401

    auth.login_as("bob")
    response = client.get('/groups/2/quizzes/')
    assert response.status_code == 403

    # the only quiz's topic
    quiz_topic = QUIZZES["quiz1"]["topic"].encode()
    update_link = b'/groups/1/quizzes/1/edit'

    # alice doesn't have any quizzes
    auth.logout()
    auth.login_as("alice")
    response = client.get('/groups/1/quizzes/')
    assert quiz_topic not in response.data
    assert update_link not in response.data

    # bob does have the only quiz
    auth.logout()
    auth.login_as("bob")
    response = client.get('/groups/1/quizzes/')
    assert quiz_topic in response.data
    assert update_link in response.data



def test_author_required(app, client, auth):
    """
    Test authorization to update/delete quizzes:
    a. the user can't modify or delete other user's quiz;
    """
    # the first quiz is ben's:
    auth.login_as('alice')
    assert client.post('/groups/1/quizzes/1/edit').status_code == 403
    assert client.post('/groups/1/quizzes/1/delete').status_code == 403



@pytest.mark.parametrize('path', (
    f'/groups/1/quizzes/{len(QUIZZES)+1}/edit',
    f'/groups/1/quizzes/{len(QUIZZES)+1}/delete',
))
def test_exists_required(client, auth, path):
    """
    If quiz with given ID doesn't exists, 404 should be returned.
    """
    auth.login_as('bob')
    assert client.post(path).status_code == 404



def test_create(client, auth, app):
    """
    The <create> view should:
    a. render and return a 200 OK status for a GET request.
    b. insert the new quiz data into the database when valid data is sent in a POST request.
    """
    auth.login_as('bob')

    # GET request should return the form to fill
    response = client.get('/groups/1/quizzes/0/edit')
    assert response.status_code == 200

    # POST request should rdirect to <update> view
    response = client.post('/groups/1/quizzes/0/edit', data=REQUEST_PAYLOAD)
    assert f'http://localhost/groups/1/quizzes/{len(QUIZZES)+1}/edit' == response.headers['Location']

    # new quiz should be in database now
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.topic == REQUEST_PAYLOAD["topic"]).first()
        assert quiz is not None



def test_delete(client, auth, app):
    """
    The <delete> view should redirect to the <index> URL
    and the quiz, its questions and options should no longer exist in the database.
    """
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.id == 1).first()
        assert quiz is not None

    auth.login_as("bob")
    response = client.post('/groups/1/quizzes/1/delete')
    assert response.headers['Location'] == 'http://localhost/groups/1/quizzes/'

    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.id == 1).first()
        assert quiz is None
        questions = db.query(Question).all()
        assert len(questions) == 0
        options = db.query(Option).all()
        assert len(options) == 0



def test_update(client, auth, app):
    """
    The <update> view should:
    a. render and return a 200 OK status for a GET request.
    b. update existing quiz data in the database when valid data is sent in a POST request.
    """
    new_topic = "New Topic"
    quiz_id = 1

    # use new quiz data to update first quiz:
    request_payload = REQUEST_PAYLOAD.copy()
    request_payload["topic"] = new_topic

    auth.login_as("bob")

    response = client.get(f'/groups/1/quizzes/{quiz_id}/edit')
    assert response.status_code == 200

    response = client.post(f'/groups/1/quizzes/{quiz_id}/edit', data=request_payload)
    assert f'http://localhost/groups/1/quizzes/{quiz_id}/edit' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        assert quiz.topic == new_topic



@pytest.mark.parametrize('path', (
    '/groups/1/quizzes/0/edit',
    '/groups/1/quizzes/1/edit',
))
def test_create_update_validate(client, auth, path):
    """
    Both <create> and <update> views should fail on invalid form data.
    """
    auth.login_as("bob")

    request_payload = REQUEST_PAYLOAD.copy()
    del request_payload["topic"] # will raise key error on request.form['topic']

    response = client.post(path, data=request_payload)
    assert b'Bad form was submitted!' in response.data
    # assert response.status_code == 400




def test_update_finalized(client, auth, app):
    """
    An error should be returned when
    a user tries to update or delete a finalized quiz.
    """
    quiz_id = 1

    auth.login_as("bob")

    # use new quiz data to update first quiz:
    request_payload = REQUEST_PAYLOAD.copy()
    request_payload["is_finalized"] = "1"
    response = client.post(f'/groups/1/quizzes/{quiz_id}/edit', data=request_payload)

    # try modifying it:
    request_payload = REQUEST_PAYLOAD.copy()
    request_payload["is_finalized"] = "0"
    request_payload["topic"] = "blablabla"

    response = client.post(f'/groups/1/quizzes/{quiz_id}/edit', data=request_payload)
    assert response.status_code == 403

    response = client.post(f'/groups/1/quizzes/{quiz_id}/delete')
    assert response.status_code == 403
