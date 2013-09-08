from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter.events import BuildMenu
from splinter_qdb.models import Quote


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Quote, 'splinter_qdb:templates/_lib#render_activity.mako')


@subscriber(BuildMenu)
def build_menu(event):
    event.add_item("quote db", 'qdb.list')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('qdb.list', '/')
    config.add_route('qdb.view', '/{id:\d+}')

    config.scan('splinter_qdb')
