from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy as sa
from quizzz.db import Base


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), unique=True, nullable=False)
    password_hash = sa.Column(sa.String(120), unique=True, nullable=False)

    @classmethod
    def from_credentials(cls, *, password, **kwargs):
        obj = cls(**kwargs)
        obj.set_password_hash(password)
        return obj

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.name)
