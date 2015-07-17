import datetime

import pytz
from sqlalchemy import (
    Column,
    ForeignKey,
    Table,
    Integer,
    UnicodeText,
    Unicode,
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
from spline.models.columns import Relationship

session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.astimezone(pytz.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=pytz.utc)


# TODO back compat
TZDateTime = UTCDateTime


# TODO this probably needs a rename too
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
    password = Column(Unicode, nullable=False)

    def can(self, scope, permission):
        for group in self.groups:
            for gp in group.group_permissions:
                if gp.scope == scope and gp.permission == permission:
                    return True
        return False


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
        backref='groups',
    )


class GroupPermission(Base):
    __tablename__ = 'group_permissions'

    id = SurrogateKeyColumn()
    group_id = Column(Integer, ForeignKey(Group.id), nullable=False, primary_key=False)
    group = relationship(Group, backref='group_permissions')
    scope = Column(Unicode)
    permission = Column(Unicode)

    # TODO but wait, this needs to be scoped to a context too; how do i do
    # that, haha.  give them all a "scope" name, and deny permission to
    # anything without one?

# TODO train of thought with database:
# - this needs a migration, obviously.  but also probably needs data.
# - creating it from scratch also needs data.
# - migrations really need to be divided into separate plugins.
# - how would alembic know which plugins to upgrade?
# - maybe creating tables from scratch should register with alembic, and then
#   it only upgrades the tables it sees already mentioned.
# - i probably need a separate utility to wrap these things.  setup, upgrade.
#   invoke, i guess?  it's python after all.
