import logging
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import notfound_view_config
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from .models import User, session
from spline.events import FrontPageActivity
from spline.events import FrontPageLayout

log = logging.getLogger(__name__)

### Core stuff

@view_config(route_name='__core__.home', request_method='GET', renderer='/home.mako')
def home(request):
    event = FrontPageActivity()
    request.registry.notify(event)

    layout = FrontPageLayout()
    request.registry.notify(layout)

    return dict(
        activity=event.sorted_activity,
        layout=layout,
    )

@view_config(route_name='__core__.login', request_method='GET', renderer='/login.mako')
def login(request):
    return dict()

@view_config(route_name='__core__.login', request_method='POST')
def login__do(request):
    from pyramid.httpexceptions import HTTPForbidden, HTTPSeeOther
    from pyramid.security import remember

    # TODO don't allow re-login, implement logout, add real auth, etc etc.

    # TODO key errors...
    username = request.POST['username']

    try:
        user = session.query(User).filter_by(name=username).one()
    except NoResultFound:
        raise HTTPForbidden(detail="you don't have an account chief")

    if True:
        headers = remember(request, user.id)
        return HTTPSeeOther(request.route_url('__core__.home'), headers=headers)
    else:
        raise HTTPForbidden


### Search

@view_config(route_name='__core__.search', renderer='/search-results.mako')
def search(request):
    raw_query = request.GET['q']

    from whoosh.index import create_in, open_dir
    from whoosh.fields import ID, DATETIME, TEXT, Schema
    from whoosh.qparser import QueryParser

    schema = Schema(
        id=ID(stored=True),
        type=ID(stored=True),
        creator_id=ID(stored=True),
        timestamp=DATETIME(),
        # TODO what about stuff with multiple contents
        # TODO what about pastebin which should really use a source-code analyzer
        content=TEXT(),
    )

    #ix = create_in('data/whoosh-index/', schema)
    #writer = ix.writer()
    # TODO cannot guarantee this dir exists
    ix = open_dir(request.registry.settings['spline.search.whoosh.path'])

    from sqlalchemy import create_engine
    from spline.models import session
    #session.bind = create_engine('postgresql:///spline?host=/nail/home/amunroe/var/run')

    from spline_pastebin.models import Paste

    query_parser = QueryParser('content', schema=schema)
    whoosh_query = query_parser.parse(raw_query)

    with ix.searcher() as searcher:
        results = searcher.search(whoosh_query, limit=10)
        num_results = len(results)
        results = [repr(res) for res in results]

    return dict(
        whoosh_results=results,
        whoosh_results_count=num_results,
    )


### Search

@view_config(route_name='__core__.search', renderer='/search-results.mako')
def search(request):
    raw_query = request.GET['q']


### Special

@view_config(context=Exception)
def exception_handler(context, request):
    log.exception(context)

    try:
        response = render_to_response(
            '/error.mako', {}, request=request)
    except Exception:
        response = Response(
            "Whoops, sorry.  Something is HILARIOUSLY wrong.",
            content_type='text/plain',
            charset='utf8')

    response.status_int = 500
    return response


@notfound_view_config(append_slash=True, renderer='/error404.mako')
def four_oh_four_handler(context, request):
    request.response.status_int = 404
    return dict(
        status=404,
    )






@view_config(route_name='__core__.feed', request_method='GET')
def feed(request):
    from spline.feature.feed import Feed
    feed = Feed(
        request=request,
        title=request.registry.settings['spline.site_title'],
    )
    feed.populate_from_subscribers()
    return feed
