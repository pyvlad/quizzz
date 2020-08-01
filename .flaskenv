FLASK_APP=quizzz
# a. Emulated email server:
# python -m smtpd -n -c DebuggingServer localhost:8025
MAIL_SERVER=localhost
MAIL_PORT=8025
# b. Real email server:
# MAIL_SERVER=smtp.mail.ru
# MAIL_PORT=465
# MAIL_USE_SSL=1
# MAIL_USERNAME=flask.python@mail.ru
# MAIL_PASSWORD=crimson99
MAIL_DEFAULT_SENDER="Фласк Питонов <flask.python@mail.ru>"
