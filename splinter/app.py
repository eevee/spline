from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from splinter.models import session

def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    config = Configurator(settings=settings)

    # Static assets
    config.add_static_view('static', 'assets', cache_max_age=3600)
    # Sass compilation
    config.include('pyramid_scss')
    config.add_route('pyscss', '/css/{css_path:[^/]+}.css')
    config.add_view(route_name='pyscss', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')

    # Routes
    config.add_route('home', '/')
    # Routes for the PASTEBIN specifically
    config.add_route('paste', '/pastes')
    config.add_route('view', '/pastes/{id:\d+}')
    config.add_route('search', '/pastes/search')

    config.scan('splinter.views')
    return config.make_wsgi_app()
