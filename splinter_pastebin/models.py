from sqlalchemy import func
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import relationship

from splinter.models import Base, User, session
from splinter.models import TZDateTime, now
from splinter.search import register_for_fulltext_search


class Paste(Base):
    __tablename__ = 'pastes'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    author_id = Column(Integer, ForeignKey(User.id), nullable=True)
    title = Column(Unicode, nullable=False)
    syntax = Column(Unicode, nullable=False)
    content = Column(UnicodeText, nullable=False)
    size = Column(Integer, nullable=False)
    lines = Column(Integer, nullable=False)

    author = relationship(User, backref='pastes')

    @property
    def nice_syntax(self):
        if not self.syntax:
            return u"plain-text"

        return self.syntax

    @property
    def nice_title(self):
        if not self.title:
            return u"unnamed " + self.nice_syntax

        return self.title

    @property
    def nice_author(self):
        if not self.author:
            return u"anon"

        return self.author.name


# TODO this should probably not be so SQLA-specific
register_for_fulltext_search(Paste, u'paste',
    creator_id=Paste.author_id,
    timestamp=Paste.timestamp,
    content=Paste.content,
)
