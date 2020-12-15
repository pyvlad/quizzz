# Settings with defaults used in production; but many of these 
# can be customized for different staging environments via
# environment variables.
import os

# security settings
# Important! 
# SECRET_KEY and WTF_CSRF_SECRET_KEY must be set as environment variables!
SECRET_KEY = os.environ["SECRET_KEY"]
WTF_CSRF_SECRET_KEY = os.environ["WTF_CSRF_SECRET_KEY"]

# database settings
DATABASE_URI = "postgresql+psycopg2://{{ ansible_user }}@/{{ project_name }}"
SQLALCHEMY_ECHO = False

# mail settings
MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or "Quizzz <no-reply@quizzz.su>"
MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") or False
MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or ""
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or ""

# app settings
QUESTIONS_PER_QUIZ = int(os.environ.get("QUESTIONS_PER_QUIZ") or 10)
OPTIONS_PER_QUESTION = int(os.environ.get("OPTIONS_PER_QUESTION") or 4)
CHAT_MESSAGES_PER_PAGE = int(os.environ.get("CHAT_MESSAGES_PER_PAGE") or 10)