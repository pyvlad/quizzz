"""
Flask-Migrate-style shortcuts for alembic commands to be used in normal workflow.
For non-common commands use alembic directly.
"""
import os, sys
import subprocess
import click
from flask.cli import AppGroup


db_cmd = AppGroup('db')


def _get_alembic_cmd():
    """ Get path to alembic command in virtual environment """
    venv_dir = os.path.dirname(os.path.abspath(sys.executable))
    alembic_cmd = os.path.join(venv_dir, "alembic")
    return alembic_cmd


@db_cmd.command('migrate')
@click.option('-m', '--message', required=True)
def db_migrate(message):
    """ Automatically generate new revision. """
    subprocess.run([_get_alembic_cmd(), "revision", "--autogenerate", "-m", message])


@db_cmd.command('upgrade')
def db_upgrade():
    """ Apply all unapplied revisions up to head. """
    subprocess.run([_get_alembic_cmd(), "upgrade", "head"])


@db_cmd.command('downgrade')
def db_downgrade():
    """ Revert the most recent revision. """
    subprocess.run([_get_alembic_cmd(), "downgrade", "-1"])