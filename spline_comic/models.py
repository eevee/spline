from datetime import datetime

import tzlocal
import pytz
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    Sequence,
    Table,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    and_,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.ext.compiler as compiler
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy.orm import foreign, remote
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import select
from sqlalchemy.sql import table

from spline.feature.core import feature_adapter
from spline.feature.feed import IFeedItem
from spline.feature.filestore import StoredFile
from spline.format import format_date
from spline.models import Base, User
from spline.models import TZDateTime, now
from spline.models.columns import ProseColumn
from spline.models.columns import Relationship
from spline.models.columns import SlugColumn
from spline.models.columns import SurrogateKeyColumn
from spline.models.columns import TitleColumn


# Special sentinel time used for queued comics when the queue is disabled
END_OF_TIME = pytz.utc.localize(datetime.max)


# XXX TODO XXX HAHA GIANT HACK, PLEASE GET THIS INTO A REAL PLACE SOMETIME
XXX_HARDCODED_TIMEZONE = pytz.timezone('America/Los_Angeles')
XXX_HARDCODED_QUEUE = '024'


def get_current_publication_date(timezone):
    """Return "today" localized to the given timezone and with the time set to
    midnight.  This is the time at which a new comic is published, from the
    publisher's perspective.
    """
    return datetime.now(timezone).replace(
        hour=0, minute=0, second=0, microsecond=0)


# Via: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views
class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable

class DropView(DDLElement):
    def __init__(self, name):
        self.name = name

@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (element.name, compiler.sql_compiler.process(element.selectable))

@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return "DROP VIEW %s" % (element.name)

def view(name, metadata, selectable):
    # Deviation from the wiki recipe -- copy the columns (into dummy columns)
    # here to avoid wacky self-referential aliasing problems such as:
    # https://bitbucket.org/zzzeek/sqlalchemy/issue/3458/super-self-referential-m2m-joins-need-to
    t = table(name, *(c.copy() for c in selectable.c))

    CreateView(name, selectable).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
    return t


# TODO i guess this is going to go away entirely, then
class Comic(Base):
    __tablename__ = 'comics'
    __scope__ = 'comic'

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

    # XXX TODO XXX HAHA GIANT HACK, PLEASE GET THIS INTO A REAL PLACE SOMETIME
    @property
    def timezone(self):
        return XXX_HARDCODED_TIMEZONE
        if self.config_timezone in pytz.all_timezones_set:
            return pytz.timezone(self.config_timezone)
        else:
            return tzlocal.get_localzone()

    @property
    def current_publication_date(self):
        """Return "today" localized to this comic's timezone and with the time
        set to midnight.  This is the time at which a new comic is published,
        from the publisher's perspective.
        """
        return datetime.now(self.timezone).replace(
            hour=0, minute=0, second=0, microsecond=0)


class GalleryFolder(Base):
    __tablename__ = 'comic_chapters'
    __table_args__ = (
        # Ensure these are only checked at the end of the transaction, because
        # otherwise it becomes very difficult to actually edit them
        UniqueConstraint('left', deferrable=True, initially='DEFERRED'),
        UniqueConstraint('right', deferrable=True, initially='DEFERRED'),
    )
    __scope__ = 'comic-chapter'

    id = SurrogateKeyColumn()
    comic_id = Column(Integer, ForeignKey(Comic.id), nullable=False)
    comic = relationship(Comic, backref='chapters')

    title = TitleColumn()
    title_slug = SlugColumn(title)

    # Nested set, whee.  Unique index created above!
    left = Column(Integer, nullable=False)
    right = Column(Integer, nullable=False)
    ancestors = relationship(
        'GalleryFolder',
        primaryjoin=(remote(left) < foreign(left)) & (foreign(right) < remote(right)),
        order_by=left.desc(),
        viewonly=True,
        uselist=True,
    )
    order = synonym('left')

_folder_parent = GalleryFolder.__table__.alias()
_folder_child = GalleryFolder.__table__.alias()
folder_parentage = view(
    'gallery_folder__parent',
    Base.metadata,
    select([_folder_child.c.id.label('child_id'), _folder_parent.c.id.label('parent_id')])
    .select_from(
        _folder_child.join(
            _folder_parent,
            and_(
                _folder_parent.c.left < _folder_child.c.left,
                _folder_child.c.right < _folder_parent.c.right,
            ),
        )
    )
    .order_by(_folder_child.c.id, _folder_parent.c.left)
    .distinct(_folder_child.c.id)
)
GalleryFolder.parent = relationship(
    GalleryFolder,
    secondary=folder_parentage,
    primaryjoin=GalleryFolder.id == folder_parentage.c.child_id,
    secondaryjoin=GalleryFolder.id == folder_parentage.c.parent_id,
    foreign_keys=[folder_parentage.c.child_id, folder_parentage.c.parent_id],
    viewonly=True,
    uselist=False,
    backref='children',
)

# TODO backcompat
ComicChapter = GalleryFolder


class GalleryItem(Base):
    __tablename__ = 'comic_pages'
    __scope__ = 'comic-page'

    id = SurrogateKeyColumn()

    # TIME IS REALLY HARD???
    # This is mostly used internally, so it can just be a pytz UTC time.
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    # date_published is used all over the dang place, though, and we want to
    # know what timezone it's supposed to be in, because that controls the date
    # it claims to be.
    date_published = Column(TZDateTime, nullable=False, index=True)
    timezone = Column(Unicode, nullable=False)

    author_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    folder_id = Column('chapter_id', ForeignKey(ComicChapter.id), nullable=False)
    chapter_id = synonym('folder_id')

    # In theory, sequential with no gaps.  We try our best.
    page_number = Column(Integer, nullable=False)
    # Unambiguous ordering of every single page ever.  Doesn't really matter
    # between comics, but we can't easily UNIQUE with a comic since there's no
    # FK in this table, so whatever.
    order = Column(Integer, nullable=False)

    title = TitleColumn()
    title_slug = SlugColumn(title)
    comment = ProseColumn()

    __table_args__ = (
        UniqueConstraint(page_number, folder_id, deferrable=True),
        UniqueConstraint(order, deferrable=True),
    )

    author = relationship(User, backref='comic_pages')
    folder = relationship(GalleryFolder, backref=backref('pages', order_by=order))
    chapter = synonym('folder')
    comic = association_proxy('folder', 'comic')

    @hybrid_property
    def local_date_published(self):
        tz = pytz.timezone(self.timezone)
        return tz.normalize(self.date_published.astimezone(tz))

    # Some words on how queuing works:
    # As little non-essential state is stored as possible.  Queued pages are
    # just those that are published in the future.  Changing the queue dates
    # merely rewrites the publication dates for all the queued items.  If the
    # queue is disabled entirely, queued items all have their publication date
    # set to END_OF_TIME.
    @hybrid_property
    def is_queued(self):
        return self.date_published > datetime.now(pytz.utc)


ComicPage = GalleryItem


# TODO it may or may not be nice to put this in core?  moving it with alembic
# will be kind of tricky, but otoh i don't know how other plugins will need this
class GalleryMedia(Base):
    __tablename__ = 'gallery_media'
    id = Column(Integer, nullable=False, primary_key=True)
    discriminator = Column(
        Enum('image', 'iframe', name='gallery_media__discriminator'),
        nullable=False,
    )
    __mapper_args__ = {'polymorphic_on': discriminator}


class GalleryMedia_Image(GalleryMedia):
    __mapper_args__ = {'polymorphic_identity': 'image'}
    image_file = Column(StoredFile, nullable=True)
    thumbnail_file = Column(StoredFile, nullable=True)


class GalleryMedia_IFrame(GalleryMedia):
    __mapper_args__ = {'polymorphic_identity': 'iframe'}
    url = Column(Unicode, nullable=True)
    height = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)


gallery_items_media = Table(
    'gallery_items_media',
    Base.metadata,
    Column('gallery_item_id', ForeignKey(GalleryItem.id), primary_key=True),
    Column('gallery_media_id', ForeignKey(GalleryMedia.id), primary_key=True),
    Column('order', Integer, Sequence('gallery_items_media_order_seq'), nullable=False, unique=True, index=True),
)
GalleryItem.media = relationship(
    GalleryMedia,
    secondary=gallery_items_media,
    order_by=gallery_items_media.c.order,
)


class ComicPageTranscript(Base):
    __tablename__ = 'comic_page_transcripts'

    page = Relationship(
        ComicPage, primary_key=True,
        backref=backref(
            'transcripts',
            collection_class=attribute_mapped_collection('language'),
        ),
    )
    language = Column(Unicode(2), primary_key=True, nullable=False)
    # TODO meld this into wiki, i guess, somehow...???
    transcript = Column(UnicodeText, nullable=False)


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

    @property
    def author_name(self):
        return self.page.author.name

    def generate_url(self, request):
        return request.resource_url(self.page)
