import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from quizzz.db import Base


class Group(Base):
    __tablename__ = "groups"

    id = sa.Column(sa.Integer, primary_key=True)

    name = sa.Column(sa.String(100), nullable=False, unique=True)
    time_created = sa.Column(sa.DateTime, server_default=func.now())
    time_updated = sa.Column(sa.DateTime, onupdate=func.now())
    invitation_code = sa.Column(sa.String(10), nullable=False, unique=True)
    confirmation_needed = sa.Column(sa.Boolean(name="confirmation_needed__bool"), default=False)

    members = relationship("Member", back_populates="group", cascade="all, delete, delete-orphan")
    messages = relationship("Message", back_populates="group", cascade="all, delete, delete-orphan")
    quizzes = relationship("Quiz", back_populates="group", cascade="all, delete, delete-orphan")
    tournaments = relationship("Tournament", back_populates="group",
        order_by="Tournament.time_created.desc()", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Group %r>" % self.name

    def populate_from_wtform(self, form):
        self.name = form.name.data
        self.invitation_code = form.invitation_code.data
        self.confirmation_needed = bool(form.confirmation_needed.data)
        return self


class Member(Base):
    __tablename__ = "members"

    id = sa.Column(sa.Integer, primary_key=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)
    time_created = sa.Column(sa.DateTime, server_default=func.now())
    time_updated = sa.Column(sa.DateTime, onupdate=func.now())
    is_disabled = sa.Column(sa.Boolean(name="is_disabled__bool"), default=False)
    is_admin = sa.Column(sa.Boolean(name="is_admin__bool"), default=False)

    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="members")

    __table_args__ = (sa.UniqueConstraint('user_id', 'group_id', name='uq_members_user_group'),)

    def __repr__(self):
        return "<Member %r of group %r>" % (self.user.name, self.group.name)
