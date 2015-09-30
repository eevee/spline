from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from spline.display.rendering import render_prose
from spline.models import User
from spline.models import session
from spline_wiki.models import WikiPage


# TODO move regular wiki pages under their own directory namespace, so other
# stuff doesn't have to worry about conflicting
# TODO figure out the set of reserved characters in wiki urls so i can add a
# suffix for translations or whatever?  or maybe just root them, i.e. stick all
# pages in /wiki/en/path/path/path.

@view_config(
    context=WikiPage,
    renderer='spline_wiki:templates/view.mako')
def wiki_view(page, request):
    # TODO wait what happens if the path is empty

    # If we got here and the URL has no trailing slash, redirect and add it.
    # (Only files and /@@foo are allowed to not have a trailing slash.)
    # TODO any cleaner way to do this, or cleaner place to do it?  i can't use
    # append_slash because core has dibs on the notfound view, and anyway i
    # want a consistent url for pages that /do/ exist too
    if not request.path.endswith('/'):
        new_url = request.path_url + '/'
        if request.query_string:
            new_url += '?'
            new_url += request.query_string
        raise HTTPMovedPermanently(location=new_url)

    if not page.exists:
        # TODO what if it exists, but is a directory, or unreadable, or etc.?
        # TODO should offer spelling suggestions...  eventually
        # TODO should examine the hierarchy to see if the parent exist, or any
        # children exist
        # TODO possibly a URL containing a dot somewhere (or @@, or whatever)
        # should not end up here?
        request.response.status_int = 404
        return render_to_response(
            'spline_wiki:templates/missing.mako',
            dict(page=page),
            request=request)

    # TODO maybe i should go through git for this too, in case the repo is
    # bare.  bare repo actually sounds like an ok idea.
    content = render_prose(page.read())

    return dict(
        page=page,
        content=content,
    )


@view_config(
    context=WikiPage,
    name='edit',
    permission='edit',
    request_method='GET',
    renderer='spline_wiki:templates/edit.mako')
def wiki_edit(page, request):
    # TODO what if it's not writable?  should we check that now?
    if page.exists:
        raw_content = page.read()
    else:
        raw_content = u''

    return dict(
        page=page,
        raw_content=raw_content,
    )


@view_config(
    context=WikiPage,
    name='edit',
    permission='edit',
    request_method='POST')
def wiki_edit__do(page, request):
    # TODO what if it's not writable?  should we check that now?
    # TODO try HARD to do something useful in the case of conflicts!
    # TODO also, notice conflicts.
    # TODO consider wiring the commit process into `transaction`

    if request.POST['action'] == 'save':
        page.write(
            request.POST['content'],
            request.user.name,
            request.user.email,
            request.POST['message'],
        )
    elif request.POST['action'] == 'propose':
        page.write(
            request.POST['content'],
            request.user.name,
            request.user.email,
            request.POST['message'],
            branch=None,
        )
    else:
        # TODO uhh
        pass

    return HTTPSeeOther(location=request.resource_url(page))


@view_config(
    context=WikiPage,
    name='history',
    request_method='GET',
    renderer='spline_wiki:templates/history.mako')
def wiki_history(page, request):
    if not page.exists:
        # TODO not sure what should be done here really
        raise HTTPNotFound

    history = page.get_history()

    if history.all_emails:
        q = (session.query(User.email, User)
            .filter(User.email.in_(history.all_emails))
        )
        history.native_email_map = dict(q)

    return dict(
        page=page,
        history=history,
    )
