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
from splinter.models.columns import SlugColumn
from splinter.models.columns import SurrogateKeyColumn
from splinter.models.columns import TitleColumn


class Comic(Base):
    __tablename__ = 'comics'

    id = SurrogateKeyColumn()
    title = TitleColumn()
    title_slug = SlugColumn(title)


class ComicChapter(Base):
    __tablename__ = 'comic_chapters'

    id = SurrogateKeyColumn()
    comic_id = Column(Integer, ForeignKey(Comic.id), nullable=False)
    title = TitleColumn()
    # TODO these slugs need to be unique /per comic/
    #title_slug = SlugColumn(title)

    comic = relationship(Comic, backref='chapters')


class ComicPage(Base):
    __tablename__ = 'comic_pages'

    id = SurrogateKeyColumn()
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    author_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chapter_id = Column(Integer, ForeignKey(ComicChapter.id), nullable=False)
    file = Column(UnicodeText, nullable=False)
    title = TitleColumn()
    # TODO these slugs need to be unique /per comic/
    #title_slug = SlugColumn(title)
    comment = Column(Prose, nullable=False)

    author = relationship(User, backref='comic_pages')
    chapter = relationship(ComicChapter, backref='pages')
    comic = association_proxy('chapter', 'comic')
