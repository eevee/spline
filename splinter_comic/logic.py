from sqlalchemy.orm import eagerload_all

from splinter.models import session
from splinter_comic.models import Comic, ComicChapter, ComicPage


def get_recent_pages():
    # TODO needs date filter for features
    return (
        session.query(ComicPage)
        .filter(~ ComicPage.is_queued)
        .order_by(ComicPage.order.desc())
        .options(
            eagerload_all(ComicPage.chapter, ComicChapter.comic)
        )
    )
