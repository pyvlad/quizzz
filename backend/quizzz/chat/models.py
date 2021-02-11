import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from quizzz.db import Base, TimeStampedModel


class Message(TimeStampedModel, Base):
    __tablename__ = 'messages'

    id = sa.Column(sa.Integer, primary_key=True)

    text = sa.Column(sa.String(1000), nullable=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)
    round_id = sa.Column(sa.Integer, sa.ForeignKey('rounds.id', ondelete='CASCADE'), nullable=True)

    user = relationship("User", back_populates="messages")
    group = relationship("Group", back_populates="messages")
    round = relationship("Round", back_populates="messages")

    def __repr__(self):
        return "<Message %r [%r]>" % (self.text[:10], self.id)
