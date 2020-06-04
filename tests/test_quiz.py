import pytest
from flask import g, session
from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.quiz.models import Quiz, Question, Option

from .data import USERS, QUIZZES, QUIZ_QUESTIONS, QUESTION_OPTIONS


REQUEST_PAYLOAD = {
    "quiz_topic": "Quiz 2",
    "question_1": "What is love?",
    "question_1_answer": "4",
    "question_1_option_1": "baby, don't hurt me",
    "question_1_option_2": "don't hurt me",
    "question_1_option_3": "no more",
    "question_1_option_4": "all of these",
    "question_2": "How much is the fish?",
    "question_2_answer": "4",
    "question_2_option_1": "lala-lalala-la-la",
    "question_2_option_2": "lalalala",
    "question_2_option_3": "lala-lalala-la-lalala",
    "question_2_option_4": "all of these",
    "is_finalized": "0"
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
    response = client.get('/groups/2/quiz/')
    assert response.status_code == 401
    
    auth.login_as("bob")
    response = client.get('/groups/2/quiz/')
    assert response.status_code == 403

    # the only quiz's topic
    quiz_topic = QUIZZES["quiz1"]["topic"].encode()
    update_link = b'href="/groups/1/quiz/1/update"'

    # alice doesn't have any quizzes
    auth.logout()
    auth.login_as("alice")
    response = client.get('/groups/1/quiz/')
    assert quiz_topic not in response.data
    assert update_link not in response.data

    # bob does have the only quiz
    auth.logout()
    auth.login_as("bob")
    response = client.get('/groups/1/quiz/')
    assert quiz_topic in response.data
    assert update_link in response.data



def test_author_required(app, client, auth):
    """
    Test authorization to update/delete quizzes:
    a. the user can't modify or delete other user's quiz;
    """
    # the first quiz is ben's:
    auth.login_as('alice')
    assert client.post('/groups/1/quiz/1/update').status_code == 403
    assert client.post('/groups/1/quiz/1/delete').status_code == 403



@pytest.mark.parametrize('path', (
    f'/groups/1/quiz/{len(QUIZZES)+1}/update',
    f'/groups/1/quiz/{len(QUIZZES)+1}/delete',
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
    response = client.get('/groups/1/quiz/create')
    assert response.status_code == 200

    # POST request should rdirect to <update> view
    response = client.post('/groups/1/quiz/create', data=REQUEST_PAYLOAD)
    assert f'http://localhost/groups/1/quiz/{len(QUIZZES)+1}/update' == response.headers['Location']

    # new quiz should be in database now
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.topic == REQUEST_PAYLOAD["quiz_topic"]).first()
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
    response = client.post('/groups/1/quiz/1/delete')
    assert response.headers['Location'] == 'http://localhost/groups/1/quiz/'

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
    # use new quiz data to update first quiz:
    request_payload = REQUEST_PAYLOAD.copy()
    request_payload["quiz_topic"] = "New Topic"

    auth.login_as("bob")

    response = client.get('/groups/1/quiz/1/update')
    assert response.status_code == 200

    # updating is done by deleting old one and adding the updated version as a new quiz
    response = client.post('/groups/1/quiz/1/update', data=request_payload)
    assert 'http://localhost/groups/1/quiz/2/update' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        quiz_old = db.query(Quiz).filter(Quiz.id == 1).first()
        assert quiz_old is None
        quiz = db.query(Quiz).filter(Quiz.id == 2).first()
        assert quiz is not None



@pytest.mark.parametrize('path', (
    '/groups/1/quiz/create',
    '/groups/1/quiz/1/update',
))
def test_create_update_validate(client, auth, path):
    """
    Both <create> and <update> views should fail on invalid form data.
    """
    auth.login_as("bob")

    request_payload = REQUEST_PAYLOAD.copy()
    del request_payload["quiz_topic"] # will raise key error on request.form['quiz_topic']

    response = client.post(path, data=request_payload)
    assert response.status_code == 400
