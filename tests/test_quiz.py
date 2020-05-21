import pytest
from flask import g, session
from quizzz.db import get_db_session
from quizzz.auth.models import User
from quizzz.quiz.models import Quiz, Question, Option


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
}


def test_models(app):
    """
    Test whether conftest objects have been inserted as expected.
    """
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).first()
        assert quiz is not None
        assert len(quiz.questions) == 2
        assert len([opt for q in quiz.questions for opt in q.options if opt.is_correct]) == 2



def test_index(client, auth):
    """
    The index view should display quizzes that the author added.
    There should be a link to edit/view the quiz.
    """
    response = client.get('/groups/1/quiz/')
    assert response.status_code == 400
    assert b'Test Quiz' not in response.data

    auth.login()
    response = client.get('/groups/1/quiz/')
    assert b'Test Quiz' in response.data
    assert b'href="/groups/1/quiz/1/update"' in response.data



def test_author_required(app, client, auth):
    """
    Test authorization to update/delete quizzes:
    a. bob user can't modify other user's post
    b. bob user doesn't see edit link
    """
    auth.login(username='bob', password='dog')
    assert client.post('/groups/1/quiz/1/update').status_code == 403
    assert client.post('/groups/1/quiz/1/delete').status_code == 403
    assert b'href="/groups/1/quiz/1/update"' not in client.get('/groups/1/quiz/').data



@pytest.mark.parametrize('path', (
    '/groups/1/quiz/3/update',
    '/groups/1/quiz/3/delete',
))
def test_exists_required(client, auth, path):
    """
    If quiz with given ID doesn't exists, 404 should be returned.
    """
    auth.login()
    assert client.post(path).status_code == 404



def test_create(client, auth, app):
    """
    The <create> view should:
    a. render and return a 200 OK status for a GET request.
    b. insert the new quiz data into the database when valid data is sent in a POST request.
    """
    auth.login(username='bob', password='dog')
    assert client.get('/groups/1/quiz/create').status_code == 200
    response = client.post('/groups/1/quiz/create', data=REQUEST_PAYLOAD)
    assert 'http://localhost/groups/1/quiz/2/update' == response.headers['Location']

    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.topic == REQUEST_PAYLOAD["quiz_topic"]).first()
        assert quiz is not None



def test_delete(client, auth, app):
    """
    The delete view should redirect to the index URL
    and the post should no longer exist in the database.
    """
    with app.app_context():
        db = get_db_session()
        quiz = db.query(Quiz).filter(Quiz.id == 1).first()
        assert quiz is not None

    auth.login()
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
    request_payload = REQUEST_PAYLOAD.copy()
    request_payload["quiz_topic"] = "New Topic"

    auth.login()
    assert client.get('/groups/1/quiz/1/update').status_code == 200
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
    Both <create> and <update> views should show an error message on invalid data.
    """
    auth.login()

    request_payload = REQUEST_PAYLOAD.copy()
    del request_payload["quiz_topic"] # will raise key error on request.form['quiz_topic']
    response = client.post(path, data=request_payload)
    assert response.status_code == 400
