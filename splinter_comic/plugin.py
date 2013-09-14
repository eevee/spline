from splinter.routing import DatabaseRouteConnector
from splinter_comic.models import Comic, ComicChapter, ComicPage

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
