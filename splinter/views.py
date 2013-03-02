import pygments
import pygments.formatters
import pygments.lexers
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from .models import Paste, User, session


@view_config(route_name='home', renderer='/new.mako')
def home(request):
    return dict(
        #guessed_name=ipmap.get(request.remote_addr, ''),
        lexers=pygments.lexers.get_all_lexers(),
    )

@view_config(route_name='paste', request_method='POST')
def do_paste(request):
    syntax = request.POST['syntax']
    if syntax == '[none]':
        syntax = ''
    elif syntax == '[auto]':
        lexer = pygments.lexers.guess_lexer(request.POST['content'])
        syntax = lexer.aliases[0]
    elif syntax.startswith('['):
        raise ValueError

    paste = Paste(
        author=request.POST.get('author', ''),
        title=request.POST.get('title', ''),
        syntax=syntax,
        content=request.POST['content'],
    )
    session.add(paste)
    session.flush()

    return HTTPSeeOther(location=request.route_url('view', id=paste.id))


@view_config(route_name='paste', renderer='/list.mako')
def list_paste(request):
    pastes = session.query(Paste) \
        .order_by(Paste.id.desc()) \
        .limit(20)

    return dict(pastes=pastes)


@view_config(route_name='view', renderer='/view.mako')
def view(request):
    paste = session.query(Paste) \
        .filter(Paste.id == request.matchdict['id']) \
        .one()

    if paste.syntax != '':
        lexer = pygments.lexers.get_lexer_by_name(paste.syntax)
    else:
        lexer = pygments.lexers.TextLexer()
    pretty_content = pygments.highlight(paste.content, lexer, pygments.formatters.HtmlFormatter())

    return dict(
        paste=paste,
        pretty_content=pretty_content,
    )


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
