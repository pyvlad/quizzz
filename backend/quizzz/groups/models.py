import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from quizzz.db import Base, TimeStampedModel


class Group(TimeStampedModel, Base):
    __tablename__ = "groups"

    id = sa.Column(sa.Integer, primary_key=True)
    
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    password = sa.Column(sa.String(20), nullable=True)
    confirmation_needed = sa.Column(sa.Boolean(name="confirmation_needed__bool"), default=False)
    max_members = sa.Column(sa.Integer)           # null means 'unlimited'

    members = relationship("Member", back_populates="group", cascade="all, delete, delete-orphan")
    messages = relationship("Message", back_populates="group", cascade="all, delete, delete-orphan")
    quizzes = relationship("Quiz", back_populates="group", cascade="all, delete, delete-orphan")
    tournaments = relationship("Tournament", back_populates="group",
        order_by="Tournament.time_created.desc()", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Group %r [%r]>" % (self.name, self.id)

    def populate_from_wtform(self, form):
        self.name = form.name.data
        self.password = form.password.data
        self.confirmation_needed = bool(form.confirmation_needed.data)
        return self


class Member(TimeStampedModel, Base):
    __tablename__ = "members"

    id = sa.Column(sa.Integer, primary_key=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    group_id = sa.Column(sa.Integer, sa.ForeignKey('groups.id'), nullable=False)
    
    is_admin = sa.Column(sa.Boolean(name="is_admin__bool"), default=False)
    is_approved = sa.Column(sa.Boolean(name="is_approved__bool"), default=True)

    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="members")

    __table_args__ = (sa.UniqueConstraint('user_id', 'group_id', name='uq_members_user_group'),)

    def __repr__(self):
        return "<Member %r [%r] of Group %r [%r]>" % (
            self.user.name, self.user_id, self.group.name, self.group_id)
