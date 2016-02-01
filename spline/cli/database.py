import sys
import getpass
import importlib
import logging

import bcrypt
import coloredlogs
from sqlalchemy import engine_from_config
import transaction

from spline.models import (
    session,
    Base,
    User,
    Group,
    GroupPermission
    )


def configure_parser(subparser):
    p_initdb = subparser.add_parser('init-db')
    p_initdb.set_defaults(func=init_db)

    p_newuser = subparser.add_parser('create-user')
    p_newuser.set_defaults(func=create_user)


def import_plugins(plugin_specs):
    plugin_list = []
    try:
        for spec in plugin_specs:
            plugin, route_prefix = spec.split(':', 1)
            importlib.import_module(plugin)
            plugin_list.append(plugin)
    except TypeError:
        pass

    return plugin_list


def _add_permission(permission, group):
    pass


def init_db(parser, args):
    settings = vars(args)

    # Logging
    # TODO this should probably go in the main entry point
    coloredlogs.install(level=logging.INFO)
    # TODO what is this for, it was debug-only, is there any reason we wouldn't want it
    #logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Plugin loading
    plugin_list = import_plugins(settings.get('spline.plugins', ()))

    engine = engine_from_config(settings, 'sqlalchemy.')
    session.configure(bind=engine)

    Base.metadata.create_all(engine, checkfirst=True)

    comic_title = settings.get('spline.comic_name')
    chapter_title = settings.get('spline.chapter_name')

    with transaction.manager:
        try:
            g = session.query(Group).filter_by(id=1).one()
        except:
            g = Group(id=1, name='admin')
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


def create_user(parser, args):
    engine = engine_from_config(vars(args), 'sqlalchemy.')
    session.configure(bind=engine)

    with transaction.manager:
        all_groups = {
            group.name: group
            for group in session.query(Group)
        }

    username = input('username: ').strip()
    email = input('email: ').strip()
    password = getpass.getpass('password: ')
    password2 = getpass.getpass('confirm password: ')

    if password != password2:
        print("passwords don't match!")
        sys.exit(1)

    group_names = []
    if all_groups:
        print()
        print("available groups: {}".format(', '.join(all_groups)))
        group_names = input('comma-separated list of groups to add to: ').strip().split(',')

    with transaction.manager:
        pwhash = bcrypt.hashpw(
            password.encode('utf8'),
            bcrypt.gensalt(14),
        ).decode('ascii')

        # TODO would be neat to have a password field that hashes on assignment
        # and does the right thing with equality check
        user = User(name=username, email=email, password=pwhash, groups=[])
        for group_name in group_names:
            user.groups.append(all_groups[group_name])
        session.add(user)
        session.flush()
        userid = user.id

    print()
    print("created user {} with id {}".format(username, userid))
