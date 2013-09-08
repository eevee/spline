from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter.events import BuildMenu
from splinter_love.models import Love


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Love, 'splinter_love:templates/_lib#render_activity.mako')


@subscriber(BuildMenu)
def build_menu(event):
    event.add_item("love", 'love.list')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('love.list', '/')
    config.add_route('love.express', '/express')

    config.scan('splinter_love')
