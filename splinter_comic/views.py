from pyramid.view import view_config

from splinter.models import session
from splinter_comic.models import ComicPage


@view_config(
    route_name='comic.index',
    request_method='GET',
    renderer='splinter_comic:templates/index.mako')
def comic_index(context, request):
    pages = (
        session.query(ComicPage)
        .order_by(ComicPage.timestamp.desc())
        .limit(10)
    )
    return dict(
        pages=pages,
    )
