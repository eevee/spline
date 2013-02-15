from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from splinter.models import Paste, session

def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    config = Configurator(settings=settings)
    config.add_static_view('static', 'assets', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('paste', '/pastes')
    config.add_route('view', '/pastes/{id:\d+}')
    config.add_route('search', '/pastes/search')
    config.scan('splinter.views')
    return config.make_wsgi_app()
