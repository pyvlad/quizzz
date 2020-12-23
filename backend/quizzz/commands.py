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
