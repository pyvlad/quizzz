from getpass import getpass

import click
from flask.cli import with_appcontext

from quizzz.db import get_db_session
from quizzz.auth.models import User


@click.command('promote-user')
@click.argument('username')
@with_appcontext
def promote_user(username):
    """
    Grant the right to create groups to a user.
    """
    db = get_db_session()
    user = db.query(User).filter(User.name == username).first()
    if user is None:
        click.echo("Fail! No such user: %s." % username)
        return
    if user.can_create_groups:
        click.echo("No changes made. User %s already has group admin rights." % username)
        return
    user.can_create_groups = True
    db.commit()
    click.echo("Success! Granted group admin rights to %s." % username)


@click.command('create-superuser')
@click.option('-u', '--username', required=True)
@click.option('-e', '--email', required=True)
@with_appcontext
def create_superuser(username, email):
    """
    Create user with the right to use admin interface.
    """
    db = get_db_session()
    user = db.query(User).filter(User.name == username).first()
    if user:
        click.echo("Fail! User <%s> already exists." % username)
        return
    
    superuser = User(name=username, email=email, is_confirmed=True, is_superuser=True)
    superuser.create_uuid()

    while True: 
        pass1 = getpass("Create password: ")
        if len(pass1) < 10:
            click.echo("Please use a longer password (10 symbols at least)")
            continue
        pass2 = getpass("Confirm password: ")
        if pass1 != pass2:
            click.echo("Passwords don't match. Try again.")
        else:
            break
    
    superuser.set_password_hash(pass1)

    db.add(superuser)
    db.commit()
    click.echo("Success! Superuser <%s> has been created." % username)