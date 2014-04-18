from collections import namedtuple

from pyramid.events import subscriber

from spline.events import FrontPageLayout
from spline.events import BuildMenu
from spline.models import session
from spline_pastebin.models import Paste


FrontPageBlock = namedtuple('FrontPageBlock', ['renderer', 'pastes'])

@subscriber(FrontPageLayout)
def find_activity(event):
    # TODO proooobably need some kinda helpful shared  date and count limit here
    # TODO start porting to logic?
    pastes = session.query(Paste).order_by(Paste.timestamp.desc()).limit(8).all()

    # TODO is this a good idea
    if pastes:
        event.blocks.append(FrontPageBlock(
            renderer='spline_pastebin:templates/_lib#front_page_block.mako',
            pastes=pastes,
        ))


@subscriber(BuildMenu)
def build_menu(event):
    event.add_item("pastes", 'pastebin.list')


def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('pastebin.list', '/')
    config.add_route('pastebin.new', '/new')
    config.add_route('pastebin.view', '/{id:\d+}')

    config.scan('spline_pastebin')
