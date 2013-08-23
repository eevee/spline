from splinter.routing import DatabaseRouteConnector
from splinter_comic.models import Comic, ComicChapter, ComicPage

def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    # TODO what goes on / now?
    drc = DatabaseRouteConnector('comic_id', Comic.id)
    config.add_route('comic.most-recent', '/{comic_id:\d+}/', **drc.kwargs)
    config.add_route('comic.upload', '/{comic_id:\d+}/upload/', **drc.kwargs)
    config.add_route('comic.archive', '/{comic_id:\d+}/archive/', **drc.kwargs)

    drc2 = drc.derive('page_id', ComicPage.id, relchain=(ComicPage.chapter, ComicChapter.comic))
    config.add_route('comic.page', '/{comic_id:\d+}/page/{page_id:\d+}/', **drc2.kwargs)

    config.scan('splinter_comic')
