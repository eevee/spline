import datetime

import pytz
from sqlalchemy import (
    Column,
    Integer,
    UnicodeText,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
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
