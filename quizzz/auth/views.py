import sqlalchemy as sa
from flask import request, session, g, redirect, url_for, flash, render_template

from quizzz.db import get_db_session
from quizzz.flashing import Flashing

from . import bp
from .models import User
from .forms import RegistrationForm, LoginForm



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

            user = User(name=username)
            user.set_password_hash(password)

            db = get_db_session()
            db.add(user)
            db.commit()

            flash(f'User {username} has been successfully created.', Flashing.SUCCESS)
            return redirect(url_for('auth.login'))
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

        db = get_db_session()
        user = db.query(User).filter(User.name == username).first()

        error = None
        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash(error, Flashing.ERROR)

    return render_template('auth/login.html', form=form)



@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
