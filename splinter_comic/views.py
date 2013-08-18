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
