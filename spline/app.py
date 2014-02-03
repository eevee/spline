from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.security import authenticated_userid
import pyramid_beaker
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from spline.events import BuildMenu
from spline.models import User, session

def get_user(request):
    userid = authenticated_userid(request)

    if userid is None:
        return None

    try:
        return session.query(User).get(userid)
    except NoResultFound:
        # TODO should this forget who you are if you don't exist?
        return None


# TODO: GET RID OF THIS THE TOOLBAR FIRES IT ONCE FOR EVERY PANEL WHOOPS
def inject_template_vars(event):
    request = event['request']

    # Query plugins for what goes on the menu
    menu = BuildMenu(request)
    request.registry.notify(menu)
    event['spline_menu'] = menu


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    session_factory = pyramid_beaker.session_factory_from_settings(settings)

    config = Configurator(settings=settings)

    # Logging
    # TODO neeed to somehow specify whether this is debug land or not; want
    # sane defaults but not always the same
    config.include('spline.lib.logging')

    # Sessions
    config.include(pyramid_beaker)
    config.set_session_factory(session_factory)

    # Auth
    config.set_authentication_policy(SessionAuthenticationPolicy(prefix='__core__.auth.'))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_request_method(get_user, 'user', reify=True)

    # Events
    config.add_subscriber(inject_template_vars, BeforeRender)

    # Static assets
    config.add_static_view('static', 'assets', cache_max_age=3600)
    config.add_static_view('filestore', '../data/filestore', cache_max_age=3600)
    # Sass compilation
    config.include('pyramid_scss')
    config.add_route('pyscss', '/css/{css_path:[^/]+}.css')
    config.add_view(route_name='pyscss', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')

    # Routes
    config.add_route('__core__.home', '/')
    config.add_route('__core__.login', '/@@login')
    config.add_route('__core__.search', '/@@search')
    config.add_route('__core__.feed', '/@@feed')


    config.scan('spline.views')
    config.scan('spline.feature')

    # Plugin loading
    for plugins in settings.get('spline.plugins', '').strip().split():
        plugin, route_prefix = plugins.split(':', 1)
        config.include(plugin, route_prefix=route_prefix)

    # Final catch-all route to defer to the wiki
    config.add_route('__core__.wiki', '/*path')

    return config.make_wsgi_app()
