from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter_love.models import Love


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Love, 'splinter_love:templates/_lib#render_activity.mako')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('love.list', '/')
    config.add_route('love.express', '/express')

    config.scan('splinter_love')
