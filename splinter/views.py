from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from .models import User, session
from splinter.events import FrontPageActivity
from splinter_pastebin.models import Paste


@view_config(route_name='pastebin.search', renderer='/search-results.mako')
def search(request):
    results = Paste.search(request.GET['q'])

    return dict(results=results)



### Core stuff

@view_config(route_name='__core__.home', request_method='GET', renderer='/home.mako')
def home(request):
    event = FrontPageActivity()
    request.registry.notify(event)

    return dict(activity=event.sorted_activity)

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
        raise HTTPForbidden(message="you don't have an account chief")

    if True:
        headers = remember(request, user.id)
        return HTTPSeeOther(request.route_url('__core__.home'), headers=headers)
    else:
        raise HTTPForbidden
