from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import authenticated_userid
import pyramid_beaker
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from splinter.models import User, session

def get_user(request):
    userid = authenticated_userid(request)

    if userid is None:
        return None

    try:
        return session.query(User).get(userid)
    except NoResultFound:
        # TODO should this forget who you are if you don't exist?
        return None


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    session_factory = pyramid_beaker.session_factory_from_settings(settings)

    config = Configurator(settings=settings)

    # Sessions
    config.include(pyramid_beaker)
    config.set_session_factory(session_factory)

    # Auth
    config.set_authentication_policy(SessionAuthenticationPolicy(prefix='__core__.auth.'))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_request_method(get_user, 'user', reify=True)

    # Static assets
    config.add_static_view('static', 'assets', cache_max_age=3600)
    # Sass compilation
    config.include('pyramid_scss')
    config.add_route('pyscss', '/css/{css_path:[^/]+}.css')
    config.add_view(route_name='pyscss', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')

    # Routes
    config.add_route('__core__.home', '/')
    config.add_route('__core__.login', '/@@login')


    config.scan('splinter.views')

    # Plugin loading
    config.include('splinter_pastebin', route_prefix='/pastes')
    config.include('splinter_love', route_prefix='/loves')

    return config.make_wsgi_app()
