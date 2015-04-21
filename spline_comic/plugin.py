from collections import namedtuple

from pyramid.events import subscriber

from spline.display.rendering import render_with_context
from spline.events import FrontPageLayout
from spline.events import BuildMenu
from spline.feature.feed import Feed
from spline.models import session
from spline.routing import DatabaseRouteConnector
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

    first_pages = get_first_pages_for_chapters(page.chapter for page in latest_pages)
    chapter_to_first_page = dict(
        (page.chapter, page)
        for page in first_pages)

    first_pages = get_first_pages_for_comics(page.comic for page in latest_pages)
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
        event.add_item("{} comic".format(comic.title), 'comic.most-recent', comic)


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
@comic_plugin.define_renderable('latest-page', 'spline_comic:templates/page#main_section.mako')
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

    config.add_route('comic.admin', '/@@admin')
    config.add_route('comic.save-queue', '/@@admin/queue')
    config.add_route('comic.upload', '/@@admin/upload')

    # TODO so where does this go, if anywhere?  really only existed to replace
    # the front page...
    config.add_route('comic.most-recent', '/most-recent/')

    drc = DatabaseRouteConnector('comic_id', Comic.title_slug)
    config.add_route('comic.browse', '/{comic_id}/', **drc.kwargs)

    # TODO oh yeah this is completely fucking wrong now.  really SHOULD have a
    # chapter in it somewhere, but the problem is that "transparent" chapters
    # would mean we sometimes have /comic/chapter/page/ and sometimes have
    # /comic/page/ and dealing with that is too hard so i'm not bothering yet.
    # maybe i want to just suck it up and allow infinite nesting here haha.  :S
    drc2 = drc.derive('page_id', ComicPage.id, slug=ComicPage.title_slug, relchain=(ComicPage.chapter, ComicChapter.comic))
    config.add_route('comic.page', '/{comic_id}/page/{page_id}/', **drc2.kwargs)

    # TODO lol this is catastrophically bad
    # TODO maybe add a method for adding more paths?  or reuse some of
    # pyramid's existing static plumbing?
    config.registry.settings['scss.asset_path'] += '\nspline_comic:assets/scss'

    config.scan('spline_comic')
