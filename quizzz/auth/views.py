import sqlalchemy as sa
from flask import request, session, g, redirect, url_for, flash, render_template

from quizzz.db import get_db_session

from . import bp
from .models import User



@bp.route('/register', methods=('GET', 'POST'))
def register():
    # redirect logged in users to home page
    if g.user:
        return redirect(url_for("index"))

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        db_session = get_db_session()

        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            user = db_session.query(User).filter(User.name == username).first()
            if user is not None:
                error = f'User {username} already exists.'

        if error is None:
            user = User(name=username)
            user.set_password_hash(password)
            db_session.add(user)
            db_session.commit()
            flash(f"User {username} has been successfully created.")
            return redirect(url_for('auth.login'))
        else:
            flash(error)

    return render_template('auth/register.html')



@bp.route('/login', methods=('GET', 'POST'))
def login():
    # redirect logged in users to home page
    if g.user:
        return redirect(url_for("index"))

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        db_session = get_db_session()

        error = None

        user = db_session.query(User).filter(User.name == username).first()
        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')



@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
