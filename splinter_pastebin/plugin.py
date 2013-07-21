from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter_pastebin.models import Paste


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Paste, 'splinter_pastebin:templates/_lib#render_activity.mako')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('pastebin.list', '/')
    config.add_route('pastebin.new', '/new')
    config.add_route('pastebin.view', '/{id:\d+}')

    config.scan('splinter_pastebin')
