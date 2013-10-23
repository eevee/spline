"""Custom Pyramid events and related helpers for plugins to hook."""

from collections import namedtuple
import operator

from pyramid.renderers import get_renderer

from splinter.models import session


class BuildMenu(object):
    """Event that asks plugins to build the primary menu."""

    def __init__(self, request):
        self.request = request

        self.menu_items = []

    def add_item(self, label, route_name, *args, **kwargs):
        self.menu_items.append((label, route_name, args, kwargs))

    def __iter__(self):
        return iter(self.menu_items)


MAX_ACTIVITY_COUNT = 30
#MAX_ACTIVITY_TIME = ...

ActivitySource = namedtuple('ActivitySource', ['source', 'timestamp', 'renderer'])

class FrontPageActivity(object):
    """Event that gathers activity for the front page.

    If your activity lives in a table with a `timestamp` column, you can
    implement this hook just by calling `event.activity_from_database`.
    Otherwise, use `add_activity` directly.
    """

    def __init__(self, max_time=None, max_count=MAX_ACTIVITY_COUNT):
        self.activity = []

        self.max_time = max_time
        self.max_count = max_count

    def add_activity(self, sources, render_function,
            timestamp_accessor=operator.attrgetter('timestamp')):
        """Register an iterable of `ActivitySource`s and a renderer string for
        rendering them.
        """
        renderer = get_renderer(render_function)
        for source in sources:
            self.activity.append(ActivitySource(
                source=source,
                timestamp=timestamp_accessor(source),
                renderer=renderer,
            ))

    def activity_from_database(self, table, render_function,
            timestamp_accessor=operator.attrgetter('timestamp')):
        """Fetch rows from the database and wrap them in `ActivitySource`s."""
        # TODO optimize the heck outta this like spline.frontpage
        q = (
            session.query(table)
            .order_by(timestamp_accessor(table).desc())
            .limit(self.max_count)
        )
        self.add_activity(q, render_function, timestamp_accessor)

    @property
    def sorted_activity(self):
        """List of all `ActivitySource`s, in temporal order starting from the
        most recent.
        """
        # TODO shouldn't need a normal sort when we can interleave
        # already-sorted items.  or maybe that's overthinking.
        self.activity.sort(key=operator.attrgetter('timestamp'), reverse=True)
        return self.activity[:self.max_count]


class FrontPageLayout(object):
    def __init__(self):
        self.blocks = []


