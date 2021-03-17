import datetime as dt
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    @property
    def id_as_str(self):
        return str(self.id)


class UserLoginHistory(Base):
    __tablename__ = 'user_login_history'
    __table_args__ = (
        Index('device_idx', 'device'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), index=True, nullable=False)
    user_agent = Column(String, nullable=False)
    device = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    fingerprint = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class SocialAccount(Base):
    __tablename__ = 'social_account'
    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship(User, backref=backref('social_accounts'))
    social_id = Column(String, nullable=False)
    social_name = Column(String, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
