from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
import pyramid_beaker
from sqlalchemy import engine_from_config

from splinter.models import session

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

    # Static assets
    config.add_static_view('static', 'assets', cache_max_age=3600)
    # Sass compilation
    config.include('pyramid_scss')
    config.add_route('pyscss', '/css/{css_path:[^/]+}.css')
    config.add_view(route_name='pyscss', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')

    # Routes
    config.add_route('home', '/')
    config.add_route('__core__.login', '/@@login')


    # Routes for LOVES specifically
    config.add_route('love.list', '/loves')
    config.add_route('love.express', '/loves/express')

    config.scan('splinter.views')

    # Plugin loading
    config.include('splinter_pastebin', route_prefix='/pastes')

    return config.make_wsgi_app()
