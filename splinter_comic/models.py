from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    UnicodeText,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from splinter.models import Base, User
from splinter.models import Prose, TZDateTime, now


class Comic(Base):
    __tablename__ = 'comics'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(Unicode, nullable=False)


class ComicChapter(Base):
    __tablename__ = 'comic_chapters'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    comic_id = Column(Integer, ForeignKey(Comic.id), nullable=False)
    title = Column(Unicode, nullable=False)

    comic = relationship(Comic, backref='chapters')


class ComicPage(Base):
    __tablename__ = 'comic_pages'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    author_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chapter_id = Column(Integer, ForeignKey(ComicChapter.id), nullable=True)
    file = Column(UnicodeText, nullable=False)
    title = Column(Unicode, nullable=False)
    comment = Column(Prose, nullable=False)

    author = relationship(User, backref='comic_pages')
    chapter = relationship(ComicChapter, backref='pages')
    comic = association_proxy('chapter', 'comic')
