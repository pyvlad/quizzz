import sqlalchemy as sa
from flask import request, session, g, redirect, url_for, flash, render_template
from . import bp
from .models import User
from quizzz.db import get_db_session



@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_session = get_db_session()

        error = None
        if not username:
            error = 'username is required'
        elif not password:
            error = 'password is required'
        else:
            user = db_session.query(User).filter(User.name == username).first()
            if user is not None:
                error = f'user {username} already exists'

        if error is None:
            user = User(name=username, password=password)
            db_session.add(user)
            db_session.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')



@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_session = get_db_session()

        error = None

        user = db_session.query(User).filter(User.name == username).first()
        if user is None:
            error = 'incorrect username'
        elif user.password != password:
            error = 'incorrect password'

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



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db_session()
        g.user = db.query(User).filter(User.id == user_id).one()
