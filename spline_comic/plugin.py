from collections import namedtuple
from functools import partial

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.events import subscriber

from spline.display.rendering import render_with_context
from spline.events import FrontPageLayout
from spline.events import BuildMenu
from spline.feature.feed import Feed
from spline.models import session
from spline_comic.logic import get_recent_pages
from spline_comic.logic import get_latest_page_per_comic
from spline_comic.logic import get_first_pages_for_chapters
from spline_comic.logic import get_first_pages_for_comics
from spline_comic.logic import get_adjacent_pages
from spline_comic.models import Comic, ComicChapter, ComicPage


FrontPageBlock = namedtuple('FrontPageBlock', [
    'renderer',
    'latest_page',
    'chapter_cover_page',
    'comic_first_page',
])


@subscriber(FrontPageLayout)
def offer_blocks(event):
    # TODO does this need a date filter too?  do something else if it's too
    # old...?
    latest_pages = get_latest_page_per_comic()

    first_pages = get_first_pages_for_chapters(
        page.chapter for page in latest_pages)
    chapter_to_first_page = dict(
        (page.chapter, page)
        for page in first_pages)

    first_pages = get_first_pages_for_comics(
        page.comic for page in latest_pages)
    comic_to_first_page = dict(
        (page.comic, page)
        for page in first_pages)

    for page in latest_pages:
        block = FrontPageBlock(
            renderer='spline_comic:templates/_lib#front_page_block.mako',
            latest_page=page,
            chapter_cover_page=chapter_to_first_page[page.chapter],
            comic_first_page=comic_to_first_page[page.comic],
        )
        event.blocks.append(block)


@subscriber(Feed)
def populate_feed(event):
    # TODO this needs date filter, limiting
    pages = get_recent_pages()
    event.add_feed_items(*pages)


@subscriber(BuildMenu)
def build_menu(event):
    # TODO can these be...  cached?  but then how would it be busted.
    # TODO order?
    # TODO this is pretty piss-poor now that "comic" has been kind of
    # overloaded to mean not really that
    for comic in session.query(Comic):
        event.add_item(
            "{} comic".format(comic.title),
            'comic.most-recent',
            comic,
        )


# Resource stuff -- violently jam my ideas into Pyramid
# TODO document, clean up a bit

# Generate URLs
class DummyResourceURL(namedtuple('_DummyResourceURL', [
        'virtual_path', 'virtual_path_tuple',
        'physical_path', 'physical_path_tuple',
        ])):
    def __new__(cls, *path_parts):
        if path_parts and path_parts[-1] != '':
            path_parts += ('',)
        # NOTE: "virtual" means the X-Vhm-Root header, which i don't care about
        path = '/' + '/'.join(path_parts)
        return super().__new__(cls, path, path_parts, path, path_parts)


def _gallery_folder_path(route_prefix, folder):
    ret = [route_prefix]
    for anc in folder.ancestors:
        ret.append(anc.title_slug)
    ret.append(folder.title_slug)
    return ret


def make_gallery_folder_url(route_prefix, folder, request):
    return DummyResourceURL(*_gallery_folder_path(route_prefix, folder))


def make_gallery_item_url(route_prefix, item, request):
    folder_path = _gallery_folder_path(route_prefix, item.folder)
    if item.title_slug:
        folder_path.append("{0.id}-{0.title_slug}".format(item))
    else:
        folder_path.append("{0.id}".format(item))
    return DummyResourceURL(*folder_path)


# Resolve URLs
def canonicalize_resource_url(request, resource):
    canon_url = request.resource_url(resource)
    if canon_url != request.path_url:
        if request.query_string:
            canon_url += '?' + request.query_string
        raise HTTPMovedPermanently(location=canon_url)


def folder_route_factory(request):
    path_parts = request.matchdict['folder_path'].split('/')
    try:
        folder = (
            session.query(ComicChapter)
            .filter_by(title_slug=path_parts[-1])
            .options(joinedload('ancestors'))
            .one()
        )
    except NoResultFound:
        raise HTTPNotFound
    else:
        canonicalize_resource_url(request, folder)
        return folder


def page_route_factory(request):
    page_id = int(request.matchdict['page_id'])
    try:
        page = (
            session.query(ComicPage)
            .filter_by(id=page_id)
            .options(joinedload('folder').joinedload('ancestors'))
            .one()
        )
    except NoResultFound:
        raise HTTPNotFound
    else:
        canonicalize_resource_url(request, page)
        return page


class Plugin:
    """Represents a plugin.

    The most convenient way to create a plugin is to use this class _as a
    metaclass_.
    """
    registry = {}

    def __init__(self, name, module):
        self.registry[name] = self

        self.name = name
        self.module = module

        # TODO this should probably be specific to the homepage, and there can
        # be other categories later (or maybe the categories should be
        # arbitrary, even).  but that doesn't matter until this feature is used
        # more
        self.renderables = {}

    # Decorators

    def configurator(self, f):
        self._configure_pyramid = f
        return f

    def define_renderable(self, *args, **kwargs):
        def decorator(f):
            self._register_renderable(f, *args, **kwargs)
            return f
        return decorator

    def _register_renderable(self, f, identifier, template_path):
        self.renderables[identifier] = (template_path, f)

    # API

    def configure_pyramid(self, config):
        return self._configure_pyramid(self, config)

    # TODO maybe this should be a method on an object that contains the
    # function and renderer path, come to think of it.
    def render(self, mako_context, request, identifier):
        renderer_path, func = self.renderables[identifier]
        namespace = func(request)
        return render_with_context(mako_context, renderer_path, **namespace)


comic_plugin = Plugin('comic', __name__)


# TODO how on earth will this still work when there are multiple comics going
# on?  currently we just inject one block for every comic which isn't going to
# work for a gallery-oriented thing either
@comic_plugin.define_renderable(
    'latest-page',
    'spline_comic:templates/page#main_section.mako')
def render_current_page(request):
    # TODO it would be nice, in theory, if there were a little plugin-scoped
    # bucket for storing data in, in case there's something expensive that
    # multiple blocks need
    latest_page = get_recent_pages().first()

    adjacent_pages = get_adjacent_pages(latest_page, include_queued=False)

    return dict(
        page=latest_page,
        adjacent_pages=adjacent_pages,
    )


@comic_plugin.configurator
def configure_comic(self, config):
    config.register_spline_plugin(self)

    # Routing
    # TODO what goes on / now?
    config.add_route('comic.archive', '/')

    # There needs to be a context for the auth thing to work, because it looks
    # at the context's __scope__ property to check for permission...  oops.
    # TODO can i fix this?  what's the context for the admin pages?  is this a
    # sign that something is just catastrophically wrong with this approach?
    # or should there be a way to handle no context at all?
    class DumbAdminPermissionHack:
        __scope__ = 'comic'

        def __init__(self, request):
            pass

    config.add_route('comic.admin', '/@@admin', factory=DumbAdminPermissionHack)
    config.add_route('comic.save-queue', '/@@admin/queue', factory=DumbAdminPermissionHack)
    config.add_route('comic.upload', '/@@admin/upload', factory=DumbAdminPermissionHack)
    config.add_route('comic.admin.folders', '/@@admin/folders', factory=DumbAdminPermissionHack)

    # TODO so where does this go, if anywhere?  really only existed to replace
    # the front page...
    config.add_route('comic.most-recent', '/most-recent/')

    # TODO one teeny problem here is that a folder whose name starts with a
    # number is completely inaccessible
    config.add_route(
        'comic.page',
        '/{folder_path:.+}/{page_id:\d+}{page_slug:(?:-[^/]*)?}/',
        factory=page_route_factory,
        use_global_views=True,
    )
    config.add_route(
        'comic.browse',
        '/{folder_path:.+}/',
        factory=folder_route_factory,
        use_global_views=True,
    )

    config.add_resource_url_adapter(
        partial(make_gallery_folder_url, config.route_prefix),
        ComicChapter,
    )
    config.add_resource_url_adapter(
        partial(make_gallery_item_url, config.route_prefix),
        ComicPage,
    )

    # TODO lol this is catastrophically bad
    # TODO maybe add a method for adding more paths?  or reuse some of
    # pyramid's existing static plumbing?
    config.registry.settings['scss.asset_path'] += '\nspline_comic:assets/scss'

    config.scan('spline_comic')
