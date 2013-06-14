from pyramid.events import subscriber

from splinter.events import FrontPageActivity
from splinter_qdb.models import Quote


@subscriber(FrontPageActivity)
def find_activity(event):
    event.activity_from_database(
        Quote, 'splinter_qdb:templates/_lib#render_activity.mako')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('qdb.list', '/')
    config.add_route('qdb.view', '/{id:\d+}')

    config.scan('splinter_qdb')
