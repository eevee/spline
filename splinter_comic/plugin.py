import operator

from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter.events import BuildMenu
from splinter.feature.feed import Feed
from splinter.models import session
from splinter.routing import DatabaseRouteConnector
from splinter_comic.logic import get_recent_pages
from splinter_comic.models import Comic, ComicChapter, ComicPage


@subscriber(FrontPageActivity)
def find_activity(event):
    # TODO this needs date filter
    pages = get_recent_pages()
    event.add_activity(
        pages[:event.max_count],
        'splinter_comic:templates/_lib#render_activity.mako',
        timestamp_accessor=operator.attrgetter('date_published'))


@subscriber(Feed)
def populate_feed(event):
    # TODO this needs date filter, limiting
    pages = get_recent_pages()
    event.add_feed_items(*pages)


@subscriber(BuildMenu)
def build_menu(event):
    # TODO can these be...  cached?  but then how would it be busted.
    # TODO order?
    for comic in session.query(Comic):
        event.add_item(comic.title, 'comic.most-recent', comic)


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    # TODO what goes on / now?
    drc = DatabaseRouteConnector('comic_id', Comic.title_slug)
    config.add_route('comic.most-recent', '/{comic_id}/', **drc.kwargs)
    config.add_route('comic.admin', '/{comic_id}/admin/', **drc.kwargs)
    config.add_route('comic.save-queue', '/{comic_id}/admin/queue/', **drc.kwargs)
    config.add_route('comic.upload', '/{comic_id}/admin/upload/', **drc.kwargs)
    config.add_route('comic.archive', '/{comic_id}/archive/', **drc.kwargs)

    drc2 = drc.derive('page_id', ComicPage.id, slug=ComicPage.title_slug, relchain=(ComicPage.chapter, ComicChapter.comic))
    config.add_route('comic.page', '/{comic_id}/page/{page_id}/', **drc2.kwargs)

    config.scan('splinter_comic')
