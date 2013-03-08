from pyramid.httpexceptions import HTTPSeeOther
from pyramid.security import Authenticated
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from .models import Love, Paste, User, session


@view_config(route_name='search', renderer='/search-results.mako')
def search(request):
    results = Paste.search(request.GET['q'])

    return dict(results=results)



### Events

from pyramid.events import BeforeRender, subscriber

# TODO need this to play more friendly with others
@subscriber(BeforeRender)
def add_ye_globals(event):
    pastes = session.query(Paste) \
        .order_by(Paste.id.desc()) \
        .limit(20)

    event['recent_pastes'] = pastes





### Core stuff

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
        return HTTPSeeOther(request.route_url('home'), headers=headers)
    else:
        raise HTTPForbidden


# TODO how on earth do i scope template vars
@subscriber(BeforeRender)
def add_ye_more_globals(event):
    from pyramid.security import authenticated_userid
    userid = authenticated_userid(event['request'])

    if userid:
        # TODO what if this fails!  auto-forget?
        user = session.query(User).get(userid)
        event['user'] = user



### Love stuff

# TODO: permission=Authenticated?  on both of these
@view_config(route_name='love.express', request_method='GET', renderer='/love/express.mako')
def express_love(request):
    return dict()

@view_config(route_name='love.express', request_method='POST')
def express_love__do(request):
    # TODO real form handling thx

    # TODO make this a request prop
    from pyramid.security import authenticated_userid
    source = session.query(User).get(authenticated_userid(request))
    # TODO error handling lol
    target = session.query(User).filter_by(name=request.POST['target']).one()

    session.add(Love(
        source=source,
        target=target,
        comment=request.POST['comment'],
    ))

    return HTTPSeeOther(request.route_url('love.list'))


@view_config(route_name='love.list', request_method='GET', renderer='/love/list.mako')
def list_love(request):
    loves = session.query(Love).order_by(Love.timestamp.desc())
    return dict(
        loves=loves,
    )

