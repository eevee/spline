import pygments
import pygments.formatters
import pygments.lexers
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config

from .models import Paste, session


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
