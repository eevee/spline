import sys
import importlib
import logging
import transaction

import coloredlogs
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from bcrypt import (
    hashpw,
    gensalt
)

from spline.lib.parsing import (
    make_parser
)

from spline.models import (
    session,
    Base,
    User,
    Group,
    GroupPermission
    )


def main(argv=sys.argv):
    parser = make_parser(True)
    args = parser.parse_args()
    initdb(**vars(args))


def initdb(**settings):

    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    config = Configurator(settings=settings)

    # Logging
    coloredlogs.install(level=logging.INFO)

    # Plugin loading
    debug = settings.get('spline.debug')
    if debug:
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    plugin_list = []
    try:
        for plugins in settings.get('spline.plugins', ()):
            plugin, route_prefix = plugins.split(':', 1)
            importlib.import_module(plugin)
            plugin_list.append(plugin)
    except TypeError:
        pass
    Base.metadata.create_all(engine, checkfirst=True)

    adm_name = settings.get('spline.admin_name')
    adm_pw = settings.get('spline.admin_pw')
    adm_email = settings.get('spline.admin_email')
    comic_title = settings.get('spline.comic_name')
    chapter_title = settings.get('spline.chapter_name')
    p = adm_pw.encode('utf8')
    pw = hashpw(p, gensalt(14))

    with transaction.manager:
        try:
            u = session.query(User).filter_by(id=1).one()
        except:
            u = User(id=1, email=adm_email, name=adm_name, password=pw.decode('ascii'))
            session.add(u)
        try:
            g = session.query(Group).filter_by(id=1).one()
        except:
            g = Group(id=1, name='admin')
            g.users.append(u)
            session.add(g)
        try:
            gp0 = session.query(GroupPermission).filter_by(id=1).one()
        except:
            gp0 = GroupPermission(id=1, scope='core', permission='admin')
            gp0.group = g
            session.add(gp0)
        # Only needed if the comic plugin is loaded
        if 'spline_comic' in plugin_list:
            from spline_comic.models import Comic, ComicChapter
            try:
                gp1 = session.query(GroupPermission).filter_by(id=1).one()
            except:
                gp1 = GroupPermission(id=1, scope='comic', permission='admin')
                gp1.group = g
                session.add(gp1)
            try:
                comic = session.query(Comic).filter_by(id=1).one()
            except:
                comic = Comic(id=1, title=comic_title, config_timezone='GMT')
                session.add(comic)
            try:
                chap = session.query(ComicChapter).filter_by(id=1).one()
            except:
                chap = ComicChapter(id=1, title=chapter_title, left=0, right=0)
                chap.comic = comic
                session.add(chap)
        # Only needed if the wiki is loaded
        if 'spline_wiki' in plugin_list:
            try:
                gp2 = session.query(GroupPermission).filter_by(id=2).one()
            except:
                gp2 = GroupPermission(id=2, scope='wiki', permission='edit')
                gp2.group = g
                session.add(gp2)
