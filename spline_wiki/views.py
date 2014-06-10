from markupsafe import Markup
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from spline.display.rendering import render_prose


@view_config(route_name='wiki', renderer='spline_wiki:templates/view.mako')
def wiki_view(page, request):
    # TODO wait what happens if the path is empty

    if not page.exists:
        # TODO what if it exists, but is a directory, or unreadable, or etc.?
        # TODO i wish this were a separate endpoint but i guess it doens't
        # matter
        # TODO should this be a 404?  i'm inclined to think so
        # TODO should offer spelling suggestions...  eventually
        # TODO should examine the hierarchy to see if the parent exist, or any
        # children exist
        # TODO should actually link to creation page lol
        return render_to_response(
            'spline_wiki:templates/missing.mako',
            dict(path=page.path),
            request=request)

    # TODO maybe i should go through git for this too, in case the repo is
    # bare.  bare repo actually sounds like an ok idea.
    content = render_prose(page.read())

    return dict(
        path=page.path,
        content=content,
    )


@view_config(
    route_name='wiki',
    name='edit',
    request_method='GET',
    renderer='spline_wiki:templates/edit.mako')
def wiki_edit(page, request):
    # TODO perms
    if not request.user:
        raise HTTPForbidden

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
    route_name='wiki',
    name='edit',
    request_method='POST')
def wiki_edit__do(page, request):
    # TODO perms
    if not request.user:
        raise HTTPForbidden

    # TODO what if it's not writable?  should we check that now?
    # TODO try HARD to do something useful in the case of conflicts!
    # TODO also, notice conflicts.
    # TODO consider wiring the commit process into `transaction`
    page.write(
        request.POST['content'],
        request.user.name,
        request.user.email,
        request.POST['message'],
    )

    return HTTPSeeOther(location=request.route_url('wiki', traverse=page.path))
