import os
import os.path
import shutil
from tempfile import NamedTemporaryFile

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config

from splinter.models import session
from splinter_comic.models import ComicPage


def get_prev_next_page(page):
    prev_page = (
        session.query(ComicPage)
        .filter(ComicPage.timestamp < page.timestamp)
        .order_by(ComicPage.timestamp.desc())
        .first()
    )
    next_page = (
        session.query(ComicPage)
        .filter(ComicPage.timestamp > page.timestamp)
        .order_by(ComicPage.timestamp.asc())
        .first()
    )

    return prev_page, next_page

@view_config(
    route_name='comic.most-recent',
    request_method='GET',
    renderer='splinter_comic:templates/page.mako')
def comic_most_recent(context, request):
    page = (
        session.query(ComicPage)
        .order_by(ComicPage.timestamp.desc())
        .first()
    )

    prev_page, next_page = get_prev_next_page(page)

    return dict(
        page=page,
        prev_page=prev_page,
        next_page=next_page,
    )

@view_config(
    route_name='comic.page',
    request_method='GET',
    renderer='splinter_comic:templates/page.mako')
def comic_page(context, request):
    page = (
        session.query(ComicPage)
        .get(int(request.matchdict['id']))
    )

    prev_page, next_page = get_prev_next_page(page)

    return dict(
        page=page,
        prev_page=prev_page,
        next_page=next_page,
    )


@view_config(
    route_name='comic.archive',
    request_method='GET',
    renderer='splinter_comic:templates/archive.mako')
def comic_archive(context, request):
    pages = session.query(ComicPage).order_by(ComicPage.timestamp.asc())

    # TODO: chapters.  how will these possibly work?  do i need to require that
    # they cover distinct consecutive spans of pages?  what if the author never
    # creates any chapters?

    return dict(
        pages=pages,
    )


@view_config(
    route_name='comic.upload',
    request_method='GET',
    renderer='splinter_comic:templates/upload.mako')
def comic_upload(context, request):
    return {}


@view_config(
    route_name='comic.upload',
    request_method='POST')
def comic_upload_do(context, request):
    # TODO validation and all that boring stuff
    fh = request.POST['file'].file

    with NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(fh, tmp)

    # TODO wire into transaction so the file gets deleted on rollback
    # TODO better picking of filenames
    # TODO ripe for being broken out into a lib
    os.rename(tmp.name, os.path.join(os.path.dirname(__file__), '../data/filestore/', os.path.basename(tmp.name)))

    page = ComicPage(
        file=os.path.basename(tmp.name),

        # TODO
        author_user_id=1,

        # TODO
        chapter_id=None,

        # TODO
        title=u'',
        comment=u'',
    )
    session.add(page)
    session.flush()

    return HTTPSeeOther(location=request.route_url('comic.page', id=page.id))
