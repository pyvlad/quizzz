import uuid

from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from quizzz.db import Base


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    uuid = sa.Column(sa.String(36), unique=True, index=True, nullable=False)
    name = sa.Column(sa.String(50), unique=True, index=True, nullable=False)
    password_hash = sa.Column(sa.String(120), unique=True, nullable=False)

    memberships = relationship("Member", back_populates="user")
    messages = relationship("Message", back_populates="user")
    quizzes = relationship("Quiz", back_populates="author")
    plays = relationship("Play", back_populates="user")

    @classmethod
    def from_credentials(cls, *, password, **kwargs):
        obj = cls(**kwargs)
        obj.set_password_hash(password)
        obj.create_uuid()
        return obj

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def create_uuid(self):
        self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return '<User %r>' % (self.name)
