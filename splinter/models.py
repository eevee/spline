import datetime

import pytz
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from sqlalchemy import types

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class TZDateTime(types.TypeDecorator):
    impl = types.DateTime

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.astimezone(pytz.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=pytz.utc)

def now():
    """Default value for time columns."""
    return datetime.datetime.now(pytz.utc)




### Core stuff

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(UnicodeText, nullable=False, unique=True, index=True)



### Love stuff

class Love(Base):
    __tablename__ = 'loves'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    source_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    target_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    comment = Column(UnicodeText, nullable=False)

    source = relationship(User,
        foreign_keys=[source_user_id],
        primaryjoin=(source_user_id == User.id),
        backref='loves_expressed')
    target = relationship(User,
        foreign_keys=[target_user_id],
        primaryjoin=(target_user_id == User.id),
        backref='loves_received')
