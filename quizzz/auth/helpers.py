from flask import render_template, current_app, g
from quizzz.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    g.db.add(token)
    g.db.commit()
    send_email(
        subject='[Quizzz] Reset Your Password',
        sender=current_app.config['MAIL_SENDER'],
        recipients=[user.email],
        text_body=render_template('auth/reset_password_email.txt', username=user.name, token_id=token.uuid),
        html_body=render_template('auth/reset_password_email.html', username=user.name, token_id=token.uuid)
    )
