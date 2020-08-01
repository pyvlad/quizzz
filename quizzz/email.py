from threading import Thread
from flask import current_app
from flask_mail import Message
from quizzz import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipients, text_body, html_body, sender=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    if sender is not None:
        msg.sender = sender
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
