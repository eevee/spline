from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import eagerload_all

from spline.models import session
from spline_comic.models import Comic, ComicChapter, ComicPage


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


class PreviousNextPager:
    def __init__(
            self, prev_by_date, next_by_date, prev_by_story, next_by_story):
        self.prev_by_date = prev_by_date
        self.next_by_date = next_by_date
        self.prev_by_story = prev_by_story
        self.next_by_story = next_by_story


def get_adjacent_pages(page, include_queued):
    if not page:
        return None, None

    q = session.query(ComicPage).join(ComicPage.chapter)
    if not include_queued:
        q = q.filter(~ ComicPage.is_queued)

    prev_by_date = (
        q
        .filter(ComicPage.date_published < page.date_published)
        .order_by(ComicPage.date_published.desc())
        .first()
    )
    next_by_date = (
        q
        .filter(ComicPage.date_published > page.date_published)
        .order_by(ComicPage.date_published.asc())
        .first()
    )

    # So, "by story" is a little more complicated.  What it really means is:
    # 1. If there's a prev/next page in this folder, use that.
    # 2. Otherwise, if there's a prev/next folder, use the
    # last/first page of it.
    # Folders are sorted by their /right/ edge so that a page in a folder comes
    # after every page in any subfolders, just like the archive view shows.
    prev_by_story = (
        q
        .filter(ComicChapter.comic_id == page.chapter.comic_id)
        .filter(or_(
            ComicChapter.right < page.chapter.right,
            and_(ComicChapter.id == page.chapter.id, ComicPage.order < page.order),
        ))
        .order_by(ComicChapter.right.desc(), ComicPage.order.desc())
        .first()
    )
    next_by_story = (
        q
        .filter(ComicChapter.comic_id == page.chapter.comic_id)
        .filter(or_(
            ComicChapter.right > page.chapter.right,
            and_(ComicChapter.id == page.chapter.id, ComicPage.order > page.order),
        ))
        .order_by(ComicChapter.right.asc(), ComicPage.order.asc())
        .first()
    )

    return PreviousNextPager(
        prev_by_date, next_by_date, prev_by_story, next_by_story)
