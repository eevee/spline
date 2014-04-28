import datetime

import pytz
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
    UnicodeText,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types

from sqlalchemy.orm import (
    relationship,
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

from spline.models.columns import IdentifierColumn
from spline.models.columns import SurrogateKeyColumn

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


# Pseudo-types, to be fleshed out later
Prose = UnicodeText



### Core stuff

class User(Base):
    __tablename__ = 'users'

    id = SurrogateKeyColumn()
    email = IdentifierColumn()
    name = IdentifierColumn()


class Group(Base):
    __tablename__ = 'groups'
    id = SurrogateKeyColumn()
    name = IdentifierColumn()

    users = relationship(
        User,
        secondary=Table(
            'user_groups', Base.metadata,
            Column('user_id', ForeignKey(User.id), nullable=False, primary_key=True),
            Column('group_id', ForeignKey(id), nullable=False, primary_key=True),
        ),
    )

