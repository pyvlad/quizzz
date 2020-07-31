import uuid
import datetime

from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from quizzz.db import Base


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    uuid = sa.Column(sa.String(36), unique=True, index=True, nullable=False)
    name = sa.Column(sa.String(50), unique=True, index=True, nullable=False)
    email = sa.Column(sa.String(120), index=True, unique=True, nullable=False)
    password_hash = sa.Column(sa.String(120), unique=True, nullable=False)
    time_created = sa.Column(sa.DateTime, server_default=func.now())
    time_updated = sa.Column(sa.DateTime, onupdate=func.now())
    is_deleted = sa.Column(sa.Boolean, default=False)

    memberships = relationship("Member", back_populates="user")
    messages = relationship("Message", back_populates="user")
    quizzes = relationship("Quiz", back_populates="author")
    plays = relationship("Play", back_populates="user")
    tokens = relationship("PasswordResetToken", back_populates="user")

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

    def get_reset_password_token(self):
        token = PasswordResetToken()
        token.create_uuid()
        token.user = self
        return token

    def __repr__(self):
        return '<User %r>' % (self.name)



class PasswordResetToken(Base):
    __tablename__ = 'tokens'

    id = sa.Column(sa.Integer, primary_key=True)
    uuid = sa.Column(sa.String(36), unique=True, index=True, nullable=False)
    time_created = sa.Column(sa.DateTime, nullable=False, server_default=func.now())
    was_used = sa.Column(sa.Boolean, default=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="tokens")

    def create_uuid(self):
        self.uuid = str(uuid.uuid4())

    def has_expired(self, valid_seconds=600):
        return datetime.datetime.utcnow() > self.time_created + datetime.timedelta(seconds=valid_seconds)

    def __repr__(self):
        return '<Token %r>' % (self.id)
