from collections import defaultdict
from datetime import datetime
from datetime import time
from datetime import timedelta
from io import BytesIO
import itertools
import os
import os.path
import re
import subprocess

from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.view import view_config
import pytz

from spline.models import session
from spline_comic.logic import get_adjacent_pages
from spline_comic.models import Comic
from spline_comic.models import ComicChapter
from spline_comic.models import ComicPage
from spline_comic.models import GalleryFolder
from spline_comic.models import GalleryItem
from spline_comic.models import GalleryMedia
from spline_comic.models import GalleryMedia_Image
from spline_comic.models import GalleryMedia_IFrame
from spline_comic.models import END_OF_TIME
from spline_comic.models import XXX_HARDCODED_QUEUE
from spline_comic.models import XXX_HARDCODED_TIMEZONE
from spline_comic.models import get_current_publication_date

FOLDER_PREVIEW_PAGE_COUNT = 7


@view_config(
    route_name='comic.most-recent',
    request_method='GET')
def comic_most_recent(request):
    page = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        # "Most recent" never includes the queue
        .filter(~ ComicPage.is_queued)
        .order_by(ComicPage.order.desc())
        .first()
    )

    comic = page.chapter.comic
    include_queued = request.has_permission('queue', comic)
    adjacent_pages = get_adjacent_pages(page, include_queued)

    # TODO this is duplicated below lol
    from spline_wiki.models import Wiki
    wiki = Wiki(request.registry.settings['spline.wiki.root'])
    transcript = wiki['!comic-pages'][str(page.id)]['en']

    ns = dict(
        comic=comic,
        page=page,
        transcript=transcript,
        adjacent_pages=adjacent_pages,
    )

    # TODO sometime maybe the landing page will be a little more interesting
    # and this can go away
    if page:
        renderer = 'spline_comic:templates/page.mako'
    else:
        renderer = 'spline_comic:templates/comic-landing.mako'

    return render_to_response(renderer, ns, request=request)


@view_config(
    route_name='comic.page',
    request_method='GET',
    renderer='spline_comic:templates/page.mako')
def comic_page(page, request):
    include_queued = request.has_permission('queue', page.comic)
    if page.is_queued and not include_queued:
        # 404 instead of 403 to prevent snooping
        return HTTPNotFound()

    adjacent_pages = get_adjacent_pages(page, include_queued)

    from spline_wiki.models import Wiki
    wiki = Wiki(request.registry.settings['spline.wiki.root'])
    transcript = wiki['!comic-pages'][str(page.id)]['en']

    return dict(
        comic=page.comic,
        page=page,
        transcript=transcript,
        adjacent_pages=adjacent_pages,
    )


@view_config(
    route_name='comic.archive',
    request_method='GET',
    renderer='spline_comic:templates/archive.mako')
def comic_archive(request):
    return _comic_archive_shared(None, request)


@view_config(
    context=GalleryFolder,
    request_method='GET',
    renderer='spline_comic:templates/archive.mako')
def comic_browse(context, request):
    return _comic_archive_shared(context, request)


def _comic_archive_shared(parent_folder, request):
    folders = (
        session.query(GalleryFolder)
        .filter(GalleryFolder.parent == parent_folder)
        .options(
            joinedload(GalleryFolder.children)
        )
        .order_by(GalleryFolder.order)
        .all()
    )
    folder_ids = [folder.id for folder in folders]
    child_folder_ids = [
        child.id for folder in folders for child in folder.children
    ]

    # XXX remove this; currently used by _base.mako and the test below
    comic = session.query(Comic).order_by(Comic.id.asc()).first()

    if request.has_permission('queue', comic):
        queued_clause = True
    else:
        queued_clause = ~GalleryItem.is_queued

    recent_pages_by_folder = defaultdict(list)
    date_range_by_folder = dict()
    page_count_by_folder = dict()
    all_seen_items = set()
    if folder_ids:
        recent_page_subq = (
            session.query(
                GalleryItem,
                func.rank().over(
                    partition_by=GalleryItem.folder_id,
                    order_by=GalleryItem.order.asc(),
                ).label('rank_first'),
                func.rank().over(
                    partition_by=GalleryItem.folder_id,
                    order_by=GalleryItem.order.desc(),
                ).label('rank_last'),
            )
            .filter(GalleryItem.folder_id.in_(folder_ids))
            .filter(queued_clause)
            .subquery()
        )
        GalleryItem_alias = aliased(GalleryItem, recent_page_subq)
        recent_page_q = (
            session.query(GalleryItem_alias)
            .filter(
                (recent_page_subq.c.rank_last <= FOLDER_PREVIEW_PAGE_COUNT) |
                (recent_page_subq.c.rank_first == 1)
            )
            .order_by(GalleryItem_alias.order.asc())
        )
        for item in recent_page_q:
            recent_pages_by_folder[item.folder].append(item)
            all_seen_items.add(item)

        # Snag the start/end dates for each folder and the number of items in
        # each
        group_q = (
            session.query(
                GalleryFolder,
                func.min(GalleryItem.date_published),
                func.max(GalleryItem.date_published),
                func.count('*')
            )
            .join(GalleryFolder.pages)
            .filter(GalleryItem.folder_id.in_(folder_ids))
            .filter(queued_clause)
            .group_by(GalleryFolder.id)
        )
        tz = XXX_HARDCODED_TIMEZONE
        for folder, mindate, maxdate, count in group_q:
            date_range_by_folder[folder] = (
                tz.normalize(mindate.astimezone(tz)),
                tz.normalize(maxdate.astimezone(tz)),
            )
            page_count_by_folder[folder] = count

    first_page_by_folder = {}
    if child_folder_ids:
        recent_page_q = (
            session.query(GalleryItem)
            .filter(GalleryItem.folder_id.in_(child_folder_ids))
            .filter(queued_clause)
            .order_by(GalleryItem.folder_id, GalleryItem.order.asc())
            .distinct(GalleryItem.folder_id)
        )
        first_page_by_folder = {
            page.folder: page
            for page in recent_page_q
        }
        all_seen_items.update(first_page_by_folder.values())

    # Eagerload media rows for every item we've seen
    (
        session.query(GalleryItem)
        .options(
            joinedload(GalleryItem.media)
        )
        .filter(GalleryItem.id.in_([item.id for item in all_seen_items]))
        .all()
    )

    return dict(
        comic=comic,
        parent_folder=parent_folder,
        folders=folders,
        recent_pages_by_folder=recent_pages_by_folder,
        first_page_by_folder=first_page_by_folder,
        date_range_by_folder=date_range_by_folder,
        page_count_by_folder=page_count_by_folder,
    )


@view_config(
    route_name='comic.archive.by-date',
    request_method='GET',
    renderer='spline_comic:templates/archive-date.mako')
def comic_archive_by_date(request):
    # XXX remove this; currently used by _base.mako
    comic = session.query(Comic).order_by(Comic.id.asc()).first()

    if request.has_permission('queue', comic):
        queued_clause = True
    else:
        queued_clause = ~GalleryItem.is_queued

    items = (
        session.query(GalleryItem)
        .order_by(GalleryItem.date_published)
        .filter(queued_clause)
        .all()
    )

    return dict(
        comic=comic,
        items=items,
    )


@view_config(
    route_name='comic.admin',
    permission='admin',
    request_method='GET',
    renderer='spline_comic:templates/admin.mako')
def comic_admin(request):
    # Figure out the starting date for the calendar.  We want to show the
    # previous four weeks, and start at the beginning of the week.
    today = get_current_publication_date(XXX_HARDCODED_TIMEZONE)
    weekday_offset = (today.weekday() - 6) % -7
    start = today + timedelta(days=weekday_offset - 7 * 4)

    # Grab "recent" pages -- any posted in the past two weeks OR in the future.
    recent_pages = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicPage.date_published >= start.astimezone(pytz.utc))
        .order_by(ComicPage.date_published.desc())
        .all()
    )

    last_queued, queue_next_date = _get_last_queued_date()
    num_queued = sum(1 for page in recent_pages if page.is_queued)

    day_to_page = {page.date_published.date(): page for page in recent_pages}

    chapters = (
        session.query(ComicChapter)
        .order_by(ComicChapter.order.asc())
        .options(
            joinedload('children')
        )
        .all()
    )

    # Express calendar in dates.  Go at least four weeks into the future, OR
    # one week beyond the last queued comic (for some padding).
    calendar_start = start.date()
    calendar_start -= timedelta(days=calendar_start.isoweekday() % 7)
    calendar_end = today.date() + timedelta(days=7 * 4)
    if day_to_page:
        calendar_end = max(calendar_end, max(day_to_page) + timedelta(days=7))

    # TODO really really really need to move configuration out of comics.  this
    # was clever but not clever enough.
    comic = session.query(Comic).order_by(Comic.id.asc()).first()

    return dict(
        comic=comic,
        chapters=chapters,
        num_queued=num_queued,
        last_queued=last_queued,
        queue_next_date=queue_next_date,

        day_to_page=day_to_page,
        calendar_start=calendar_start,
        calendar_end=calendar_end,
    )


# TODO this is crap
def _get_last_queued_date():
    queued_q = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicPage.is_queued)
    )

    last_queued = queued_q.order_by(ComicPage.date_published.desc()).first()

    if last_queued:
        queue_end_date = last_queued.date_published
    else:
        queue_end_date = datetime.combine(
            get_current_publication_date(XXX_HARDCODED_TIMEZONE).astimezone(pytz.utc),
            time(),
        )
    if queue_end_date == END_OF_TIME:
        queue_next_date = None
    else:
        weekdays = [int(wd) for wd in XXX_HARDCODED_QUEUE]
        queue_next_date = next(_generate_queue_dates(weekdays, start=queue_end_date))

    return last_queued, queue_next_date


def _generate_queue_dates(days_of_week, start):
    if not days_of_week:
        # Special case: an empty queue means to freeze the queue, which is
        # easily done in practice by dating everything into the far future
        while True:
            yield END_OF_TIME

    days_of_week = set(days_of_week)
    delta = timedelta(days=1)

    d = start
    dow = d.weekday()

    # NB: Never consider today as part of the queue
    while True:
        d += delta
        dow = (dow + 1) % 7

        if dow in days_of_week:
            yield d


@view_config(
    route_name='comic.save-queue',
    permission='admin',
    request_method='POST')
def comic_queue_do(request):
    # TODO this would be easier with a real validator.
    weekdays = []
    for wd in request.POST.getall('weekday'):
        if wd in '0123456':
            weekdays.append(int(wd))

    queued = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicPage.is_queued)
        .order_by(ComicPage.order.asc())
        .all()
    )

    new_dates = _generate_queue_dates(weekdays, start=get_current_publication_date(XXX_HARDCODED_TIMEZONE))
    for page, new_date in zip(queued, new_dates):
        page.date_published = datetime.combine(
            new_date, time()).replace(tzinfo=pytz.utc)
        page.timezone = XXX_HARDCODED_TIMEZONE.zone

    comic.config_queue = ''.join(str(wd) for wd in sorted(weekdays))

    # TODO flash message?
    return HTTPSeeOther(location=request.route_url('comic.admin', comic))


@view_config(
    route_name='comic.upload',
    permission='admin',
    request_method='POST')
def comic_upload_do(request):
    # TODO validation and all that boring stuff
    file_upload = request.POST['file']
    fh = file_upload.file

    from spline.feature.filestore import IStorage
    storage = request.registry.queryUtility(IStorage)

    _, ext = os.path.splitext(file_upload.filename)
    filename = storage.store(fh, ext)
    # TODO ha ha this is stupid
    # TODO very skinny images shouldn't be blindly made 200x200
    fh.seek(0)
    thumb = subprocess.check_output(['convert', '-', '-resize', '200x200', '-'], stdin=fh)
    # TODO this interface is bad also
    thumbname = storage.store(BytesIO(thumb), ext)

    # TODO wire into transaction so the file gets deleted on rollback

    last_chapter = (
        session.query(ComicChapter)
        .filter(ComicChapter.id == int(request.POST['chapter']))
        .one()
    )

    when = request.POST['when']
    if when == 'now':
        date_published = datetime.now(pytz.utc)
    elif when == 'queue':
        last_queued, queue_next_date = _get_last_queued_date()
        date_published = datetime.combine(
            queue_next_date,
            time(tzinfo=XXX_HARDCODED_TIMEZONE),
        )
        date_published = date_published.astimezone(pytz.utc)

    # Fetch next page number and ordering.  Also need to shift everyone else
    # forwards by one if this is bumping the queue.  Blurgh.
    max_order, = (
        session.query(func.max(ComicPage.order))
        .filter(ComicPage.date_published <= date_published)
        .first()
    )
    if max_order is None:
        max_order = 0
    next_order = max_order + 1

    (
        session.query(ComicPage)
        .filter(ComicPage.order >= next_order)
        .update({ComicPage.order: ComicPage.order + 1})
    )

    max_page_number, = (
        session.query(func.max(ComicPage.page_number))
        .with_parent(last_chapter)
        .filter(ComicPage.date_published <= date_published)
        .first()
    )
    if max_page_number is None:
        max_page_number = 0
    next_page_number = max_page_number + 1

    (
        session.query(ComicPage)
        .with_parent(last_chapter)
        .filter(ComicPage.page_number >= next_page_number)
        .update({ComicPage.page_number: ComicPage.page_number + 1})
    )

    page = ComicPage(
        chapter=last_chapter,
        author=request.user,
        date_published=date_published,
        timezone=XXX_HARDCODED_TIMEZONE.zone,

        order=next_order,
        page_number=next_page_number,

        # TODO more validation here too
        title=request.POST['title'],
        comment=request.POST['comment'],

        media=[
            GalleryMedia_Image(
                image_file=os.path.basename(filename),
                thumbnail_file=os.path.basename(thumbname),
            )
        ],
    )

    if request.POST.get('iframe_url'):
        url = request.POST['iframe_url']
        # If it's a YouTube URL, convert to the embed URL automatically
        # TODO this seems like a neat thing to do for many other services and
        # make a tiny library out of, if it's not done already?
        # TODO why doesn't this use urlparse???
        m = re.match(
            '^(?:https?://)?(?:www[.])?youtube[.]com/watch[?]v=([-_0-9a-zA-Z]+)(?:&|$)',
            url)
        if m:
            url = "https://www.youtube.com/embed/{}?rel=0".format(m.group(1))

        m = re.match('^(?:https?://)?youtu[.]be/([-_0-9a-zA-Z]+)(?:[?]|$)', url)
        if m:
            url = "https://www.youtube.com/embed/{}?rel=0".format(m.group(1))

        try:
            width = int(request.POST['iframe_width'])
        except (KeyError, ValueError):
            width = 800
        try:
            height = int(request.POST['iframe_height'])
        except (KeyError, ValueError):
            height = 600

        page.media.append(GalleryMedia_IFrame(
            url=url, width=width, height=height))

    session.add(page)
    session.flush()

    return HTTPSeeOther(location=request.resource_url(page))


@view_config(
    route_name='comic.admin.folders',
    permission='admin',
    request_method='POST')
def comic_admin_folders_do(request):
    folder = session.query(ComicChapter).get(request.POST['folder_id'])
    action = request.POST['action']
    # Prevent accidents
    return HTTPSeeOther(
        location=request.route_url('comic.admin') + '#manage-folders')

    # TODO this should verify, somehow, that there's actually something to the left or right to move to
    # TODO ha ha this doesn't work if the chosen folder has children, dummy!
    if direction == "left":
        # Move the folder leftwards, so that its new "right" is one less than its current "left"
        diff = (folder.left - 1) - folder.right
    elif direction == "right":
        # Move the folder rightwards, so that its new "left" is one more than its current "right"
        diff = (folder.right + 1) - folder.left
    else:
        raise HTTPBadRequest

    # TODO this assumes one direction only...  or does it?
    (
        session.query(ComicChapter)
        .filter(ComicChapter.left.between(
            *sorted((folder.left, folder.left + diff))))
        .update({
            ComicChapter.left: ComicChapter.left - diff,
            ComicChapter.right: ComicChapter.right - diff,
        }, synchronize_session=False)
    )

    folder.left += diff
    folder.right += diff

    return HTTPSeeOther(
        location=request.route_url('comic.admin') + '#manage-folders')


@view_config(
    route_name='comic.admin.folders.new',
    permission='admin',
    request_method='POST')
def comic_admin_folders_new_do(request):
    # TODO error checking...  might be no POSTs, for example
    folder = session.query(GalleryFolder).get(request.POST['relativeto'])
    if not folder:
        # TODO
        raise HTTPBadRequest

    where = request.POST['where']
    if where == 'before':
        # "Before" really means taking its place, so the target folder and
        # every subsequent folder should scoot forwards two places
        left = folder.left
    elif where == 'after':
        # New folder's left should immediately follow the target folder's right
        left = folder.right + 1
    elif where == 'child':
        # New folder should go where its parents' current right is -- in case
        # there are already children, this puts the new folder last
        left = folder.right
    else:
        # TODO
        raise HTTPBadRequest

    # Shift any endpoints after the new left ahead by 2.  This will cover both
    # ancestors and unrelated folders that are further along
    (
        session.query(GalleryFolder)
        .filter(GalleryFolder.left >= left)
        .update({
            GalleryFolder.left: GalleryFolder.left + 2,
        }, synchronize_session=False)
    )
    (
        session.query(GalleryFolder)
        .filter(GalleryFolder.right >= left)
        .update({
            GalleryFolder.right: GalleryFolder.right + 2,
        }, synchronize_session=False)
    )

    # Create the new folder
    # TODO title has to be unique, non-blank, or somethin
    session.add(GalleryFolder(
        title=request.POST['title'],
        left=left,
        right=left + 1,
        # TODO temporary hack until i get rid of comics entirely
        comic_id=folder.comic_id,
    ))

    return HTTPSeeOther(
        location=request.route_url('comic.admin') + '#manage-folders')
