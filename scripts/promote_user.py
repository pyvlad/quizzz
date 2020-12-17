"""
Grant a user the right to create groups.
"""
import argparse
from quizzz import create_app
from quizzz.db import get_db_session
from quizzz.auth.models import User


def main():
    parser = argparse.ArgumentParser(description='Grant group admin rights to a user')
    parser.add_argument('-u', '--user', help="Which user to promote.", required=True)
    opts = parser.parse_args()

    app = create_app()
    with app.app_context():
        db = get_db_session()
        user = db.query(User).filter(User.name == opts.user).first()
        if user is None:
            print("No such user.")
            return
        user.can_create_groups = True
        db.commit()
        print("Granted group admin rights to %s" % user)


if __name__ == "__main__":
    main()
