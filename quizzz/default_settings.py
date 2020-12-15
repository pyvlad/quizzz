# Default settings used for development
# Production settings should override these in config.py of the instance
# This is a configuration file, from Flask docs:
# "The configuration files themselves are actual Python files. 
#  Only values in uppercase are actually stored in the config object 
#  later on. So make sure to use uppercase letters for your config keys."

# security settings
SECRET_KEY = "dev"
WTF_CSRF_SECRET_KEY = "dev"
SESSION_COOKIE_SAMESITE = "Lax"

# database settings
DATABASE_URI = ''   # need to know app instance path 
SQLALCHEMY_ECHO = True

# setting below assume emulated email server
MAIL_SERVER = "localhost"
MAIL_PORT = 8025
MAIL_USE_SSL = False
MAIL_USE_TLS = False
MAIL_USERNAME = ""
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = "Quizzz <quizzz@example.com>"

# app settings
QUESTIONS_PER_QUIZ = 2
OPTIONS_PER_QUESTION = 4
CHAT_MESSAGES_PER_PAGE = 2
PASSWORD_RESET_TOKEN_VALIDITY = 600