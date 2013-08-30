from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter.events import BuildMenu
from splinter_pastebin.models import Paste


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Paste, 'splinter_pastebin:templates/_lib#render_activity.mako')


@subscriber(BuildMenu)
def build_menu(event):
    event.add_item("pastes", 'pastebin.list')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('pastebin.list', '/')
    config.add_route('pastebin.new', '/new')
    config.add_route('pastebin.view', '/{id:\d+}')

    config.scan('splinter_pastebin')
