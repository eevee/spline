from datetime import datetime

import tzlocal
import pytz
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    UnicodeText,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from spline.feature.core import feature_adapter
from spline.feature.feed import IFeedItem
from spline.format import format_date
from spline.models import Base, User
from spline.models import Prose, TZDateTime, now
from spline.models.columns import SlugColumn
from spline.models.columns import SurrogateKeyColumn
from spline.models.columns import TitleColumn


# Special sentinel time used for queued comics when the queue is disabled
END_OF_TIME = pytz.utc.localize(datetime.max)


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

    # Time zone to use for figuring out when "midnight" is, for queue purposes
    # TODO how should this be scoped?  per-comic?  per-comic inheriting from a
    # global default?  per-site?  ?????
    config_timezone = Column(Unicode, nullable=True)

    @property
    def timezone(self):
        if self.config_timezone in pytz.all_timezones_set:
            tz = pytz.timezone(self.config_timezone)
        else:
            tz = tzlocal.get_localzone()

    @property
    def current_publication_date(self):
        """Return "today" localized to this comic's timezone and with the time
        set to midnight.  This is the time at which a new comic is published,
        from the publisher's perspective.
        """
        return datetime.now(self.timezone).replace(
            hour=0, minute=0, second=0, microsecond=0)


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
    date_published = Column(TZDateTime, nullable=False, index=True)
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
    # set to END_OF_TIME.
    @hybrid_property
    def is_queued(self):
        return self.date_published > now()


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
        ret = u"New {0} comic for {1}".format(
            self.page.comic.title, format_date(self.page.date_published))
        if self.page.title:
            ret += u": " + self.page.title
        return ret
