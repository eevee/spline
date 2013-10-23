from pyramid.events import subscriber

from spline.events import FrontPageActivity
from spline.events import BuildMenu
from spline_qdb.models import Quote


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Quote, 'spline_qdb:templates/_lib#render_activity.mako')


@subscriber(BuildMenu)
def build_menu(event):
    event.add_item("quote db", 'qdb.list')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('qdb.list', '/')
    config.add_route('qdb.view', '/{id:\d+}')

    config.scan('spline_qdb')
