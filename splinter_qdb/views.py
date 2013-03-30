from pyramid.view import view_config

from splinter.models import session
from splinter_qdb.models import Quote


@view_config(route_name='qdb.list', request_method='GET', renderer='splinter_qdb:templates/list.mako')
def quote_list(request):
    quotes = session.query(Quote).order_by(Quote.timestamp.desc())
    return dict(
        quotes=quotes,
    )
