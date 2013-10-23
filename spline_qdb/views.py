from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from spline.models import session
from spline_qdb.models import Quote


@view_config(route_name='qdb.list', request_method='GET', renderer='spline_qdb:templates/list.mako')
def quote_list(request):
    quotes = session.query(Quote).order_by(Quote.timestamp.desc())
    return dict(
        quotes=quotes,
    )

@view_config(route_name='qdb.view', request_method='GET', renderer='spline_qdb:templates/view.mako')
def quote_view(request):
    quote = session.query(Quote).get(request.matchdict['id'])

    if not quote:
        return HTTPNotFound()

    return dict(
        quote=quote,
    )
