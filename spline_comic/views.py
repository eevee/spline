from datetime import timedelta
import os
import os.path
import shutil
from tempfile import NamedTemporaryFile

from sqlalchemy import func
from sqlalchemy.orm import contains_eager
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from spline.models import now
from spline.models import session
from spline_comic.models import ComicChapter
from spline_comic.models import ComicPage
from spline_comic.models import END_OF_TIME


def get_prev_next_page(page, include_queued):
    if not page:
        return None, None

    prev_page = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic_id == page.comic.id)
        .filter(ComicPage.order < page.order)
        .order_by(ComicPage.order.desc())
        .first()
    )
    next_page = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic_id == page.comic.id)
        .filter(ComicPage.order > page.order)
        .order_by(ComicPage.order.asc())
        .first()
    )

    if next_page and next_page.is_queued and not include_queued:
        next_page = None

    return prev_page, next_page


@view_config(
    route_name='comic.most-recent',
    request_method='GET')
def comic_most_recent(comic, request):
    page = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        # "Most recent" never includes the queue
        .filter(~ ComicPage.is_queued)
        .order_by(ComicPage.order.desc())
        .first()
    )

    # TODO permissions
    include_queued = bool(request.user)
    prev_page, next_page = get_prev_next_page(page, include_queued)

    ns = dict(
        comic=comic,
        page=page,
        prev_page=prev_page,
        next_page=next_page,
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
    renderer='spline_comic:templates/archive.mako')
def comic_archive(comic, request):
    q = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .filter(ComicChapter.comic == comic)
        .order_by(ComicPage.order.asc())
        .options(contains_eager(ComicPage.chapter))
    )

    if not request.user:
        # TODO permissions
        q = q.filter(~ ComicPage.is_queued)

    pages_by_chapter = {}
    for page in q:
        pages_by_chapter.setdefault(page.chapter, []).append(page)
    chapters = list(pages_by_chapter.keys())
    chapters.sort(key=lambda chapter: chapter.id)

    return dict(
        comic=comic,
        pages_by_chapter=pages_by_chapter,
        chapters=chapters,
    )


@view_config(
    route_name='comic.admin',
    request_method='GET',
    renderer='spline_comic:templates/admin.mako')
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

    chapters = (
        session.query(ComicChapter)
        .with_parent(comic)
        # TODO should actually order by latest addition...  or maybe first?
        .order_by(ComicChapter.id.desc())
        .all()
    )

    return dict(
        comic=comic,
        chapters=chapters,
        num_queued=num_queued,
        last_queued=last_queued,
        queue_next_date=queue_next_date,
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
        queue_end_date = comic.current_publication_date
    if queue_end_date == END_OF_TIME:
        queue_next_date = None
    else:
        weekdays = [int(wd) for wd in comic.config_queue]
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

    new_dates = _generate_queue_dates(weekdays, start=comic.current_publication_date)
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

    last_chapter = (
        session.query(ComicChapter)
        .filter(ComicChapter.id == int(request.POST['chapter']))
        .one()
    )

    when = request.POST['when']
    if when == 'now':
        date_published = now()
    elif when == 'queue':
        last_queued, queue_next_date = _get_last_queued_date(comic)
        date_published = queue_next_date

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
        file=os.path.basename(tmp.name),
        chapter=last_chapter,
        author=request.user,
        date_published=date_published,

        order=next_order,
        page_number=next_page_number,

        # TODO more validation here too
        title=request.POST['title'],
        comment=request.POST['comment'],
    )
    session.add(page)
    session.flush()

    return HTTPSeeOther(location=request.route_url('comic.page', page))
