from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Unicode,
    UnicodeText,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from splinter.feature.core import feature_adapter
from splinter.feature.feed import IFeedItem
from splinter.models import Base, User
from splinter.models import Prose, TZDateTime, now
from splinter.models.columns import SlugColumn
from splinter.models.columns import SurrogateKeyColumn
from splinter.models.columns import TitleColumn


def current_publication_date():
    """Return a date object for "today", from the point of view of the queue
    system.
    """
    return datetime.utcnow().date()


class Comic(Base):
    __tablename__ = 'comics'

    id = SurrogateKeyColumn()
    title = TitleColumn()
    # This one needs to be unique because it's used alone in URLs
    title_slug = SlugColumn(title, unique=True)

    # String of digits, 0 through 6, listing the weekdays on which queued pages
    # are published.  Not actually used for the queue system; only remembers
    # the last values set in the admin UI.
    # TODO make a quick custom type or wrapper or whatever that makes this a
    # set in python-land
    config_queue = Column(Unicode, nullable=False, default=u'')


class ComicChapter(Base):
    __tablename__ = 'comic_chapters'

    id = SurrogateKeyColumn()
    comic_id = Column(Integer, ForeignKey(Comic.id), nullable=False)
    title = TitleColumn()
    title_slug = SlugColumn(title)

    comic = relationship(Comic, backref='chapters')


class ComicPage(Base):
    __tablename__ = 'comic_pages'

    id = SurrogateKeyColumn()
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    date_published = Column(Date, nullable=False, index=True)
    author_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chapter_id = Column(Integer, ForeignKey(ComicChapter.id), nullable=False)
    file = Column(UnicodeText, nullable=False)
    title = TitleColumn()
    title_slug = SlugColumn(title)
    comment = Column(Prose, nullable=False)

    author = relationship(User, backref='comic_pages')
    chapter = relationship(ComicChapter, backref='pages')
    comic = association_proxy('chapter', 'comic')

    @hybrid_property
    def order(self):
        # Some value that indicates the ordering of comics.  This should
        # maaaybe be its own column later, but for now this expresses the
        # intent in a query
        return self.timestamp

    # Some words on how queuing works:
    # As little non-essential state is stored as possible.  Queued pages are
    # just those that are published in the future.  Changing the queue dates
    # merely rewrites the publication dates for all the queued items.  If the
    # queue is disabled entirely, queued items all have their publication date
    # set to date.max.
    # TODO: currently the notion of "today" is based on UTC; unclear if this
    # should be changed to the author's time zone, or what
    @hybrid_property
    def is_queued(self):
        return self.date_published > current_publication_date()


@feature_adapter(ComicPage, IFeedItem)
class ComicPage_FeedItem(object):
    def __init__(self, page):
        self.page = page

    @property
    def timestamp(self):
        # TODO well.
        return self.page.date_published

    @property
    def title(self):
        return self.page.title
