import datetime


NOW = datetime.datetime.utcnow()
LATER = datetime.datetime.utcnow() + datetime.timedelta(hours=1)


QUIZ_REQUEST_PAYLOAD = {
    "topic": "Quiz 2",
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


TOURNAMENT_REQUEST_PAYLOAD = {
    "tournament_name": "Tournament 2",
    "is_active": True
}


ROUND_REQUEST_PAYLOAD = {
    "quiz_id": 1,
    "start_time": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "finish_time": LATER.strftime("%Y-%m-%dT%H:%M:%SZ")
}


VALID_PLAY_DATA = {
    "questions-0-question_id": "1",
    "questions-0-answer": "4",
    "questions-1-question_id": "2",
    "questions-1-answer": "8"
}
