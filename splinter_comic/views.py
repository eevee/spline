from future_builtins import zip

from datetime import date
from datetime import timedelta
import os
import os.path
import shutil
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config

from splinter.models import session
from splinter_comic.models import ComicChapter
from splinter_comic.models import ComicPage
from splinter_comic.models import current_publication_date


def get_prev_next_page(page, include_queued):
    prev_page = (
        session.query(ComicPage)
        .filter(ComicPage.chapter_id == page.chapter_id)
        .filter(ComicPage.timestamp < page.timestamp)
        .order_by(ComicPage.timestamp.desc())
        .first()
    )
    next_page = (
        session.query(ComicPage)
        .filter(ComicPage.chapter_id == page.chapter_id)
        .filter(ComicPage.timestamp > page.timestamp)
        .order_by(ComicPage.timestamp.asc())
        .first()
    )

    if next_page.is_queued and not include_queued:
        next_page = None

    return prev_page, next_page

@view_config(
    route_name='comic.most-recent',
    request_method='GET',
    renderer='splinter_comic:templates/page.mako')
def comic_most_recent(comic, request):
    page = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        # "Most recent" never includes the queue
        .filter(~ ComicPage.is_queued)
        .order_by(ComicPage.timestamp.desc())
        .first()
    )

    # TODO permissions
    include_queued = bool(request.user)
    prev_page, next_page = get_prev_next_page(page, include_queued)

    return dict(
        comic=page.comic,
        page=page,
        prev_page=prev_page,
        next_page=next_page,
    )

@view_config(
    route_name='comic.page',
    request_method='GET',
    renderer='splinter_comic:templates/page.mako')
def comic_page(page, request):
    # TODO permissions
    if page.is_queued and not request.user:
        # 404 instead of 403 to prevent snooping
        return HTTPNotFound()

    # TODO permissions
    include_queued = bool(request.user)
    prev_page, next_page = get_prev_next_page(page, include_queued)

    return dict(
        comic=page.comic,
        page=page,
        prev_page=prev_page,
        next_page=next_page,
    )


@view_config(
    route_name='comic.archive',
    request_method='GET',
    renderer='splinter_comic:templates/archive.mako')
def comic_archive(comic, request):
    q = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        .order_by(ComicPage.order.desc())
    )

    normal_pages = q.filter(~ ComicPage.is_queued)

    # TODO permissions
    # TODO collapse to one query
    if request.user:
        queued_pages = q.filter(ComicPage.is_queued)
    else:
        queued_pages = None

    # TODO: chapters.  how will these possibly work?  do i need to require that
    # they cover distinct consecutive spans of pages?  what if the author never
    # creates any chapters?

    return dict(
        comic=comic,
        pages=normal_pages,
        queue=queued_pages,
    )


@view_config(
    route_name='comic.admin',
    request_method='GET',
    renderer='splinter_comic:templates/admin.mako')
def comic_admin(comic, request):
    # TODO permissions
    if not request.user:
        return HTTPForbidden()

    queued_q = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        .filter(ComicPage.is_queued)
    )

    last_queued, queue_next_date = _get_last_queued_date(comic)
    num_queued = queued_q.count()
    return dict(
        comic=comic,
        num_queued=num_queued,
        last_queued=last_queued,
        queue_next_date=queue_next_date
    )


# TODO this is crap
def _get_last_queued_date(comic):
    queued_q = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        .filter(ComicPage.is_queued)
    )

    last_queued = queued_q.order_by(ComicPage.date_published.desc()).first()

    if last_queued:
        queue_end_date = last_queued.date_published
    else:
        queue_end_date = current_publication_date()
    if queue_end_date == date.max:
        queue_next_date = None
    else:
        weekdays = [int(wd) for wd in comic.config_queue]
        queue_next_date = next(_generate_queue_dates(weekdays, start=queue_end_date))

    return last_queued, queue_next_date

def _generate_queue_dates(days_of_week, start=None):
    if not days_of_week:
        # Special case: an empty queue means to freeze the queue, which is
        # easily done in practice by dating everything into the far future
        while True:
            yield date.max

    days_of_week = set(days_of_week)
    delta = timedelta(days=1)

    if start is None:
        d = current_publication_date()
    else:
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
    request_method='POST')
def comic_queue_do(comic, request):
    # TODO permissions
    if not request.user:
        return HTTPForbidden()

    # TODO this would be easier with a real validator.
    weekdays = []
    for wd in request.POST.getall('weekday'):
        if wd in '0123456':
            weekdays.append(int(wd))

    queued = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        .filter(ComicPage.is_queued)
        .order_by(ComicPage.order.asc())
        .all()
    )

    new_dates = _generate_queue_dates(weekdays)
    for page, new_date in zip(queued, new_dates):
        page.date_published = new_date

    comic.config_queue = ''.join(str(wd) for wd in sorted(weekdays))

    # TODO flash message?
    return HTTPSeeOther(location=request.route_url('comic.admin', comic))


@view_config(
    route_name='comic.upload',
    request_method='POST')
def comic_upload_do(comic, request):
    # TODO permissions
    if not request.user:
        return HTTPForbidden()

    # TODO validation and all that boring stuff
    fh = request.POST['file'].file

    with NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(fh, tmp)

    # TODO wire into transaction so the file gets deleted on rollback
    # TODO better picking of filenames
    # TODO ripe for being broken out into a lib
    os.rename(tmp.name, os.path.join(os.path.dirname(__file__), '../data/filestore/', os.path.basename(tmp.name)))

    # TODO yeah no.
    # ...well actually this might be a good idea to keep weird chapter churn
    # down initially, until i figure out how else that'll work
    last_chapter = (
        session.query(ComicChapter)
        .filter(ComicChapter.comic == comic)
        # XXX order by id is bad
        .order_by(ComicChapter.id.asc())
        .scalar()
    )

    when = request.POST['when']
    if when == 'now':
        date_published = current_publication_date()
    elif when == 'queue':
        last_queued, queue_next_date = _get_last_queued_date(comic)
        date_published = queue_next_date

    page = ComicPage(
        file=os.path.basename(tmp.name),
        chapter=last_chapter,
        author=request.user,
        date_published=date_published,

        # TODO more validation here too
        title=request.POST['title'],
        comment=request.POST['comment'],
    )
    session.add(page)
    session.flush()

    return HTTPSeeOther(location=request.route_url('comic.page', page))
