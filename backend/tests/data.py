USERS = {
    "bob": {
        "id": 1,
        "name": "bob",
        "password": "dog",
        "email": "bob@example.com",
        "is_confirmed": True,
    },
    "alice": {
        "id": 2,
        "name": "alice",
        "password": "cat",
        "email": "alice@example.com",
        "is_confirmed": True,
    },
    "ben": {
        "id": 3,
        "name": "ben",
        "password": "frog",
        "email": "ben@example.com",
        "is_confirmed": True,
    },
    "lucy": {
        "id": 4,
        "name": "lucy",
        "password": "pony",
        "email": "lucy@example.com",
        "is_confirmed": True, 
    }
}


GROUPS = {
    "group1": {
        "id": 1,
        "name": "group1",
        "password": "code1",
        "max_members": None
    },
    "group2": {
        "id": 2,
        "name": "group2",
        "password": "code2",
        "max_members": 3
    }
}


MEMBERSHIPS = [
    {
        "user_id": USERS["bob"]["id"],
        "group_id": GROUPS["group1"]["id"],
        "is_admin": True
    },
    {
        "user_id": USERS["alice"]["id"],
        "group_id": GROUPS["group1"]["id"]
    },
    {
        "user_id": USERS["alice"]["id"],
        "group_id": GROUPS["group2"]["id"]
    },
    {
        "user_id": USERS["ben"]["id"],
        "group_id": GROUPS["group2"]["id"]
    }
]


MESSAGES = [
    {
        "id": 1,
        "text": "group1 message from bob",
        "user_id": USERS["bob"]["id"],
        "group_id": GROUPS["group1"]["id"]
    },
    {
        "id": 2,
        "text": "group1 message from alice",
        "user_id": USERS["alice"]["id"],
        "group_id": GROUPS["group1"]["id"]
    },
    {
        "id": 3,
        "text": "group2 message from alice",
        "user_id": USERS["alice"]["id"],
        "group_id": GROUPS["group2"]["id"]
    }
]


QUIZZES = {
    "quiz1": {
        "id": 1,
        "topic": "Quiz One",
        "author_id": USERS["bob"]["id"],
        "group_id": GROUPS["group1"]["id"]
    }
}


QUIZ_QUESTIONS = {
    "question1": {
        "id": 1,
        "quiz_id": QUIZZES["quiz1"]["id"],
        "text": "What does 2+2 equal to?",
        "comment": "That's a toughie. But you can verify the answer with your fingers."
    },
    "question2": {
        "id": 2,
        "quiz_id": QUIZZES["quiz1"]["id"],
        "text": "What does the fox say?",
        "comment": "Try searching the answer on youtube.",
    }
}


QUESTION_OPTIONS = [
    {"id": 1, "text": "1", "question_id": QUIZ_QUESTIONS["question1"]["id"]},
    {"id": 2, "text": "2", "question_id": QUIZ_QUESTIONS["question1"]["id"]},
    {"id": 3, "text": "3", "question_id": QUIZ_QUESTIONS["question1"]["id"]},
    {"id": 4, "text": "4", "question_id": QUIZ_QUESTIONS["question1"]["id"], "is_correct": True},
    {"id": 5, "text": "Meaow", "question_id": QUIZ_QUESTIONS["question2"]["id"]},
    {"id": 6, "text": "Woof", "question_id": QUIZ_QUESTIONS["question2"]["id"]},
    {"id": 7, "text": "Bazinga!", "question_id": QUIZ_QUESTIONS["question2"]["id"]},
    {"id": 8, "text": "None of these", "question_id": QUIZ_QUESTIONS["question2"]["id"], "is_correct": True}
]


TOURNAMENTS = {
    "tournament1": {
        "id": 1,
        "name": "Tournament1",
        "group_id": GROUPS["group1"]["id"],
        "is_active": True,
    }
}
