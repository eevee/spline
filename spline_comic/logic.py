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


def get_latest_page_per_comic():
    """Return a list of the latest (publicly visible) page in each comic, one
    per comic.
    """
    latest_pages_subq = (
        session.query(
            Comic.id.label('comic_id'),
            func.max(ComicPage.order).label('latest_page_order'),
        )
        .select_from(ComicPage)
        .join(ComicPage.chapter)
        .join(ComicChapter.comic)
        .filter(~ ComicPage.is_queued)
        .group_by(Comic.id)
        .subquery()
    )

    latest_pages_q = (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .join(ComicChapter.comic)
        .join(
            latest_pages_subq,
            Comic.id == latest_pages_subq.c.comic_id,
        )
        .filter(ComicPage.order == latest_pages_subq.c.latest_page_order)
        # TODO more well-defined ordering?
        .order_by(Comic.id.asc())
        .options(contains_eager(ComicPage.chapter, ComicChapter.comic))
    )

    return latest_pages_q.all()


def get_first_pages_for_chapters(chapters):
    # TODO seems like it would be nice to accept a chapter query here too?
    chapter_ids = [chapter.id for chapter in chapters]

    first_pages_subq = (
        session.query(
            ComicChapter.id.label('chapter_id'),
            # TODO this doesn't really work if order isn't unique
            func.min(ComicPage.order).label('first_page_order'),
        )
        .select_from(ComicPage)
        .join(ComicPage.chapter)
        .join(ComicChapter.comic)
        .filter(~ ComicPage.is_queued)
        .group_by(ComicChapter.id)
        .subquery()
    )

    return (
        session.query(ComicPage)
        .join(
            first_pages_subq,
            ComicPage.chapter_id == first_pages_subq.c.chapter_id,
        )
        .filter(ComicPage.order == first_pages_subq.c.first_page_order)
        .filter(ComicPage.chapter_id.in_(chapter_ids))
        .all()
    )


def get_first_pages_for_comics(comics):
    # TODO seems like it would be nice to accept a chapter query here too?
    comic_ids = [comic.id for comic in comics]

    first_pages_subq = (
        session.query(
            Comic.id.label('comic_id'),
            func.min(ComicPage.order).label('first_page_order'),
        )
        .select_from(ComicPage)
        .join(ComicPage.chapter)
        .join(ComicChapter.comic)
        .filter(~ ComicPage.is_queued)
        .group_by(Comic.id)
        .subquery()
    )

    return (
        session.query(ComicPage)
        .join(ComicPage.chapter)
        .join(
            first_pages_subq,
            ComicChapter.comic_id == first_pages_subq.c.comic_id,
        )
        .filter(ComicPage.order == first_pages_subq.c.first_page_order)
        .filter(ComicChapter.comic_id.in_(comic_ids))
        .all()
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

    # TODO humble suggestion: perhaps ordering by date should order by, you know...  date?
    prev_by_date = (
        q
        .filter(ComicPage.order < page.order)
        .order_by(ComicPage.order.desc())
        .first()
    )
    next_by_date = (
        q
        .filter(ComicPage.order > page.order)
        .order_by(ComicPage.order.asc())
        .first()
    )

    # So, "by story" is a little more complicated.  What it really means is:
    # 1. If there's a prev/next page in this folder, use that.
    # 2. Otherwise, if there's a prev/next folder, use the
    # last/first page of it.
    prev_by_story = (
        q
        .filter(ComicChapter.comic_id == page.chapter.comic_id)
        .filter(or_(
            ComicChapter.order < page.chapter.order,
            and_(ComicChapter.id == page.chapter.id, ComicPage.order < page.order),
        ))
        .order_by(ComicChapter.order.desc(), ComicPage.order.desc())
        .first()
    )
    next_by_story = (
        q
        .filter(ComicChapter.comic_id == page.chapter.comic_id)
        .filter(or_(
            ComicChapter.right > page.chapter.right,
            and_(ComicChapter.id == page.chapter.id, ComicPage.order > page.order),
        ))
        .order_by(ComicChapter.order.asc(), ComicPage.order.asc())
        .first()
    )

    return PreviousNextPager(
        prev_by_date, next_by_date, prev_by_story, next_by_story)
