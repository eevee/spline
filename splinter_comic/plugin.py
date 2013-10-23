from collections import namedtuple

from pyramid.events import subscriber

from splinter.events import FrontPageLayout
from splinter.events import BuildMenu
from splinter.feature.feed import Feed
from splinter.models import session
from splinter.routing import DatabaseRouteConnector
from splinter_comic.logic import get_recent_pages
from splinter_comic.logic import get_latest_page_per_comic
from splinter_comic.logic import get_first_pages_for_chapters
from splinter_comic.logic import get_first_pages_for_comics
from splinter_comic.models import Comic, ComicChapter, ComicPage


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
            renderer='splinter_comic:templates/_lib#front_page_block.mako',
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
