import sqlalchemy as sa
from flask import request, session, g, redirect, url_for, flash, render_template, current_app

from quizzz.flashing import Flashing

from . import bp
from .models import User, PasswordResetToken
from .forms import RegistrationForm, LoginForm, RequestResetPasswordForm, ResetPasswordForm
from .helpers import send_password_reset_email, send_confirmation_email



@bp.route('/register', methods=('GET', 'POST'))
def register():
    # redirect logged in users to home page
    if g.user:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate():
            username = form.username.data.lower()
            password = form.password.data
            email = form.email.data.lower() # TODO: case sensitivity? special chars: +.?

            user = User(name=username, email=email)
            user.set_password_hash(password)
            user.create_uuid()

            g.db.add(user)
            g.db.commit()

            send_confirmation_email(user)
            flash('A confirmation email has been sent to you by email. '
                'Check your inbox/spam folder and click on the link there to complete registration.',
                Flashing.MESSAGE)
            # flash(f'User {username} has been registered!', Flashing.SUCCESS)
            session['user_id'] = user.uuid

            return redirect(url_for('index'))
        else:
            flash("Please fix the errors and submit the form again.", Flashing.ERROR)

    return render_template('auth/register.html', form=form)



@bp.route('/login', methods=('GET', 'POST'))
def login():
    # redirect logged in users to home page
    if g.user:
        return redirect(url_for("index"))

    form = LoginForm()

    if request.method == 'POST' and form.validate():
        username = form.username.data.lower()
        password = form.password.data

        user = g.db.query(User).filter(User.name == username).first()

        error = None
        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.uuid

            next = request.args.get("next", None)
            if next:
                return redirect(next)
            else:
                return redirect(url_for('index'))
        else:
            flash(error, Flashing.ERROR)

    return render_template('auth/login.html', form=form)



@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if g.user:
        return redirect(url_for('index'))

    form = RequestResetPasswordForm()

    if form.validate_on_submit():
        user = g.db.query(User).filter(User.email==form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
        flash('Instructions to reset your password have been sent to your email.')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', form=form)



@bp.route('/reset_password/<token_id>', methods=['GET', 'POST'])
def reset_password(token_id):
    if g.user:
        return redirect(url_for('index'))

    token = g.db.query(PasswordResetToken).filter_by(uuid=token_id).first()
    if token is None:
        flash("The link for password reset was broken.", Flashing.ERROR)
        return redirect(url_for('index'))

    if token.has_expired(valid_seconds=current_app.config["PASSWORD_RESET_TOKEN_VALIDITY"]):
        flash("The link for password reset has expired.", Flashing.ERROR)
        return redirect(url_for('index'))

    if token.was_used:
        flash("The link for password reset cannot be used more than once.", Flashing.ERROR)
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = token.user
        user.set_password_hash(form.password.data)
        token.was_used = True
        g.db.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)



@bp.route('/confirm/<token>')
def confirm(token):
    if not g.user:
        flash("You need to be logged in to confirm your email.")
        return redirect(url_for('auth.login', next=url_for('auth.confirm', token=token)))
    if g.user and g.user.is_confirmed:
        flash("Your email is already confirmed.")
        return redirect(url_for('index'))

    user_uuid = User.get_user_uuid_from_confirmation_token(token)
    if user_uuid and g.user.uuid == user_uuid:
        user = g.db.query(User).filter_by(uuid=user_uuid).first()
        user.is_confirmed = True
        g.db.add(user)
        g.db.commit()
        flash('Your email has been confirmed. Welcome to Quizzz!', Flashing.SUCCESS)
    else:
        flash('The confirmation link is invalid or has expired.', Flashing.ERROR)

    return redirect(url_for('index'))



@bp.route('/confirm')
def resend_confirm():
    if not g.user:
        flash("You need to be logged in to request confirmation email.")
    elif g.user and g.user.is_confirmed:
        flash("Your account is already confirmed.")
    else:
        send_confirmation_email(g.user)
        flash('A new confirmation email has been sent to you. Check your inbox/spam folder '
            'and click on the link there to complete registration.', Flashing.SUCCESS)
    return redirect(url_for('index'))



@bp.route('/unconfirmed')
def unconfirmed():
    if not g.user or (g.user and g.user.is_confirmed):
        return redirect(url_for('index'))
    return render_template('auth/unconfirmed.html')
