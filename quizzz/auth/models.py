import sqlalchemy as sa
from quizzz.db import Base


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), unique=True, nullable=False)
    password_hash = sa.Column(sa.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % (self.name)
