import argparse
import shlex
__author__ = 'Rafael Lopez'


class ShlexArgumentParser(argparse.ArgumentParser):
    """Trivial subclass that overrides how from-file args are parsed."""
    def convert_arg_line_to_args(self, arg_line):
        """To make these files not a nightmare to maintain, two changes are
        made here:

        1. Each line is fed through shlex.split().  So if you want to use
        spaces or quotes, you MUST quote or escape them.
        2. Comments (lines beginning with optional whitespace and then a #) are
        ignored.
        """
        arg_line = arg_line.strip()
        if arg_line.startswith('#'):
            return []

        return shlex.split(arg_line)


def parse_bind(s):
    """Parse a bind string and return keyword arguments appropriate for
    feeding to `waitress.serve`.
    """
    if s.startswith('unix:'):
        path = s[5:]
        if not path:
            raise argparse.ArgumentTypeError('must provide a socket path')
        return dict(unix_socket=path)

    # OK, must be host:port
    addr, _colon, strport = s.rpartition(':')
    if not _colon:
        raise argparse.ArgumentTypeError(
            'syntax: host:port or unix:/foo/bar')

    port = int(strport)
    if ':' in addr:
        if addr[0] != '[' or addr[-1] != ']':
            raise argparse.ArgumentTypeError(
                'IPv6 addresses must be enclosed in square brackets')
        addr = addr[1:-1]

    return dict(host=addr, port=port)


def make_parser(initdb=False):
    parser = ShlexArgumentParser(
        description="Run the Spline web app.",
        fromfile_prefix_chars='@',
    )
    if not initdb:
        parser.add_argument('bind', metavar='bind', nargs='?', type=parse_bind,
                        help='what to bind to, either host:port or unix://path')
    parser.add_argument('--dev', action='store_true', dest='spline.debug',
                        help='run in development mode')
    parser.add_argument('--db', metavar='database-url', dest='sqlalchemy.url',
                        required=True,
                        help='SQLAlchemy-style URL to your database')

    # TODO this could totally be in the db or wherever as long as the app can
    # restart itself after changing it
    parser.add_argument('-P', '--plugin', action='append', dest='spline.plugins',
                        help='one or more plugins to load, in the form `name:path`')
    if not initdb:
        parser.add_argument('--data-dir', required=True, dest='spline.datadir',
                        help='directory for storing a pile of disk-backed data')

    # TODO this should /definitely/ be db-backed lol
    parser.add_argument('--site-title', default='spline', dest='spline.site_title',
                        help='name of your website')

    # Initializedb specific parameters
    parser.add_argument('--admin-name', default='admin', dest='spline.admin_name',
                        help='name of the original admin account')
    parser.add_argument('--admin-pw', default='test', dest='spline.admin_pw',
                        help='password of the original admin account')
    parser.add_argument('--admin-email', default='mail@domain.com', dest='spline.admin_email',
                        help='password of the original admin account')
    parser.add_argument('--comic-name', default='My first comic', dest='spline.comic_name',
                        help='title of your first comic')
    parser.add_argument('--chapter-name', default='My first chapter', dest='spline.chapter_name',
                        help='title of the first chapter of your comic')

    return parser