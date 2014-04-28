from browserid import RemoteVerifier
from browserid.errors import TrustError
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.security import forget, remember
from pyramid.view import view_config

from spline.models import User, session

### Auth

# TODO should this be split out??
# TODO should this be made semi-generic so auth things can be added with very
# simple plugins?

@view_config(route_name='__core__.auth.login', request_method='GET', renderer='/login.mako')
def login(request):
    return dict()


@view_config(route_name='__core__.auth.login', request_method='POST')
def login__do(request):
    from pyramid.httpexceptions import HTTPForbidden, HTTPSeeOther

    # TODO don't allow re-login (replay attack where someone hits back+f5,
    # solved by switching to a new session on login/logout and invalidating the
    # old one)
    # TODO haha this still doesn't actually ask for a password.

    # TODO key errors...
    username = request.POST['username']

    try:
        user = session.query(User).filter_by(name=username).one()
    except NoResultFound:
        raise HTTPForbidden(detail="you don't have an account chief")

    if True:
        headers = remember(request, user.id)
        # TODO return to same url?
        return HTTPSeeOther(request.route_url('__core__.home'), headers=headers)
    else:
        raise HTTPForbidden


@view_config(route_name='__core__.auth.logout', request_method='POST', renderer='json')
def logout__do(request):
    headers = forget(request)
    request.session.pop('pending_auth')

    # TODO a thought: persona's global logout only works if you actually visit
    # a page with the persona js in it; if you still have the cookie, you're
    # still logged in.  maybe we should do a check on the last time you
    # requested a whole html page...?

    # TODO return to same url?
    return_url = request.route_url('__core__.home')
    if request.is_xhr:
        request.response.headerlist.extend(headers)
        return dict(
            success=True,
            redirect=return_url,
        )
    else:
        return HTTPSeeOther(return_url, headers=headers)


# TODO csrf here plz -- also everywhere.
@view_config(route_name='__core__.auth.persona.login', renderer='json')
def login(request):
    # Verify the assertion and get the email of the user
    verifier = RemoteVerifier([request.host_url])
    try:
        data = verifier.verify(request.POST['assertion'])
    except (ValueError, TrustError) as exc:
        log.exception("Bad Persona login: {!r}".format(exc))
        raise HTTPBadRequest("Invalid Persona assertion!")
    email = data['email']

    # Now either log us in immediately, or redirect to the registration page
    try:
        user = session.query(User).filter_by(email=email).one()
    except NoResultFound:
        request.session['pending_auth'] = dict(
            persona_email=email,
            return_to=request.POST['came_from'],
        )

        return dict(
            success=True,
            redirect=request.route_url('__core__.auth.register'),
        )
    else:
        request.response.headers.extend(remember(request, user.id))
        return dict(
            redirect=request.POST['came_from'],
            success=True,
        )


#@view_config(
#    route_name='__core__.auth.persona.verify',


@view_config(
    route_name='__core__.auth.register',
    request_method='GET',
    renderer='/register.mako')
def register(request):
    # TODO any better way to handle these clearly-inappropriate cases?
    if request.user or 'pending_auth' not in request.session:
        return HTTPSeeOther(location=request.route_url('__core__.home'))

    return {}

@view_config(
    route_name='__core__.auth.register',
    request_method='POST')
def register__do(request):
    # TODO check for duplicate username haha.
    # TODO and er duplicate email, which is less likely to happen i suppose
    user = User(
        email=request.session['pending_auth']['persona_email'],
        name=request.POST['username'],
    )
    session.add(user)
    session.flush()

    url = request.session['pending_auth']['return_to']
    # TODO this is the sort of thing that should only happen if the transaction
    # succeeds otherwise!
    del request.session['pending_auth']

    return HTTPSeeOther(
        location=url,
        headers=remember(request, user.id),
    )


# TODO forgot password or whatever
