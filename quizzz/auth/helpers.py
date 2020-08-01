from flask import render_template, g
from quizzz.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    g.db.add(token)
    g.db.commit()
    send_email(
        subject='[Quizzz] Reset Your Password',
        recipients=[user.email],
        text_body=render_template('auth/reset_password_email.txt', username=user.name, token_id=token.uuid),
        html_body=render_template('auth/reset_password_email.html', username=user.name, token_id=token.uuid)
    )


def send_confirmation_email(user):
    token = user.generate_confirmation_token()
    send_email(
        subject='[Quizzz] Confirm Your Account',
        recipients=[user.email],
        text_body=render_template('auth/confirmation_email.txt', username=user.name, token=token),
        html_body=render_template('auth/confirmation_email.html', username=user.name, token=token),
    )
