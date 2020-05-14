import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from quizzz.db import Base


class Group(Base):
    __tablename__ = "groups"

    id = sa.Column(sa.Integer, primary_key=True)

    created = sa.Column(sa.DateTime, server_default=func.now())
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    invitation_code = sa.Column(sa.String(10), nullable=False, unique=True)
    confirmation_needed = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return "<Group %r>" % self.name


class Member(Base):
    __tablename__ = "members"

    id = sa.Column(sa.Integer, primary_key=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)
    is_admin = sa.Column(sa.Boolean, default=False)

    user = relationship("User", backref="memberships")
    group = relationship("Group", backref="members")

    def __repr__(self):
        return "<Member %r of group %r>" % (self.user.name, self.group.name)
