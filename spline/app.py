import os
from pathlib import Path

from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.security import authenticated_userid
import pyramid_beaker
from sqlalchemy import engine_from_config

from spline.events import BuildMenu
from spline.models import User, session
from spline.web.auth import DatabaseAuthenticationPolicy
from spline.web.auth import RoleAuthorizationPolicy


def authenticate_userid(userid, request):
    if userid is None:
        return None

    # TODO should this forget who you are if you don't exist?
    return session.query(User).get(userid)


# TODO: GET RID OF THIS THE TOOLBAR FIRES IT ONCE FOR EVERY PANEL WHOOPS
def inject_template_vars(event):
    request = event['request']

    # Query plugins for what goes on the menu
    menu = BuildMenu(request)
    request.registry.notify(menu)
    event['spline_menu'] = menu


def config_register_spline_plugin(config, plugin):
    config.registry.spline_plugins[plugin.name] = plugin


# TODO this is still in progress -- splitting the core stuff into a plugin as
# well
def core_plugin_includeme(config):
    # Routes
    # TODO i'm increasingly unsure about using @@ for everything but also i
    # don't want to clobber any routes the wiki might use.
    config.add_route('__core__.home', '/')
    config.add_route('__core__.search', '/@@search')
    config.add_route('__core__.feed', '/@@feed')

    config.add_route('__core__.auth.login', '/@@auth/login/')
    config.add_route('__core__.auth.logout', '/@@auth/logout/')
    config.add_route('__core__.auth.register', '/@@auth/register/')

    config.add_route('__core__.api.render-markdown', '/api/render-markdown/')

    config.scan('spline.views')
    config.scan('spline.feature')


def main(global_settings, **settings):
    # TODO this doesn't actually work as a paste entry point, because the ini
    # values need converting  :S
    datadir = Path(settings['spline.datadir'])

    # Built-in core settings we have to have.  These are part of the app
    # propert and it makes zero sense for either a deployer or a developer to
    # ever change them.
    # TODO is this where this kind of thing should go?  seems, y'know, clunky
    settings.update({
        'pyramid.default_locale_name': u'en',
        'mako.directories': ['spline:templates'],
        'mako.module_directory': str(datadir / '_mako_cache'),
        'mako.strict_undefined': True,

        # TODO: should not need to hardcode a weird archetype path here  :)
        # TODO i am not thrilled that only a string works here
        # TODO: pyramid_scss should learn to do asset specs in imports as well,
        # but scss needs import hooking for that to work
        'scss.asset_path':
            'spline:assets/scss\n' +
            os.path.join(os.getcwd(), '../archetype.git/scss'),

        # These are reversed in debug mode
        # TODO scss should really be built and served directly in production
        'scss.compress': True,
        'scss.cache': True,
    })

    # Prefill some paths for stuff stored on disk.
    # TODO this is pretty grody  :)
    # TODO this should be a little more organized and enforce that the
    # directories exist and are writable by us -- or at least that the datadir
    # itself is?
    settings.update({
        'spline.search.whoosh.path': str(datadir / 'whoosh-index'),
        'spline.wiki.root': str(datadir / 'wiki'),

        # TODO this is all going away, i think.  lol CHANGEME.  what is that
        # even for?
        'session.type': 'file',
        'session.data_dir': str(datadir / 'sessions/data'),
        'session.lock_dir': str(datadir / 'sessions/lock'),
        'session.secret': 'CHANGEME',
        'session.cookie_on_exception': True,
    })

    debug = settings.get('spline.debug')
    if debug:
        settings.update({
            # TODO maybe i want to turn these on...  why didn't i?
            'pyramid.debug_authorization': True,
            'pyramid.debug_notfound': True,
            'pyramid.debug_routematch': True,

            'pyramid.reload_templates': True,
            'scss.compress': False,
            'scss.cache': False,
        })

    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    session_factory = pyramid_beaker.session_factory_from_settings(settings)

    config = Configurator(settings=settings)
    if debug:
        # TODO only if importable?
        config.include('pyramid_debugtoolbar')
    config.include('pyramid_tm')

    config.include('pyramid_mako')

    from spline.feature.filestore import IStorage, FilesystemStorage
    filestore_dir = (datadir / 'filestore').resolve()
    config.registry.registerUtility(FilesystemStorage(filestore_dir), IStorage)
    config.add_static_view('filestore', str(filestore_dir))

    # Logging
    # TODO neeed to somehow specify whether this is debug land or not; want
    # sane defaults but not always the same
    config.include('spline.lib.logging')

    # Sessions
    config.include(pyramid_beaker)
    config.set_session_factory(session_factory)

    # Auth
    config.set_authentication_policy(DatabaseAuthenticationPolicy())
    config.set_authorization_policy(RoleAuthorizationPolicy())
    config.add_request_method(authenticated_userid, 'user', reify=True)

    # Events
    config.add_subscriber(inject_template_vars, BeforeRender)

    # Static assets
    config.add_static_view('static', 'spline:assets', cache_max_age=3600)

    # Load core stuff first
    config.include(core_plugin_includeme)

    # Plugin loading
    # TODO this could totally be inside the app proper, as long as i know how
    # to restart myself.  mamayo problem?
    # TODO there are really two steps here, of scanning and then importing.
    # but i doubt the web app itself wants to scan just to import, right?
    # TODO now there's both a plugin dict here AND a "registry" in the Plugin
    # class itself (which is still in spline_comic btw) -- which is correct?
    # TODO SIGH should i just give up and use setuptools fucking entry points
    # TODO or actually maybe i should be taking advantage of zope things here
    # -- you can have named implementations of an interface after all!
    config.registry.spline_plugins = {}
    config.add_directive(
        'register_spline_plugin', config_register_spline_plugin)
    for plugins in settings.get('spline.plugins', ()):
        plugin, route_prefix = plugins.split(':', 1)
        config.include(plugin, route_prefix=route_prefix)

    # Sass compilation
    # TODO this has to appear after the includes, or pyramid_scss won't see any
    # additional paths added.  needs a real api for doing that
    config.include('pyramid_scss')
    config.add_route('pyscss', '/css/{css_path:[^/]+}.css')
    config.add_view(route_name='pyscss', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')

    return config.make_wsgi_app()
