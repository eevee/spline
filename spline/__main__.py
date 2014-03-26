"""Entry point for running spline as a web app."""
# NOTE: this code CANNOT EVER go in spline/app.py; running that directly will
# change its name to __main__ which will make pyramid confused and unhappy.
import argparse

import waitress

import spline.app


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


def make_parser():
    parser = argparse.ArgumentParser(
        description="Run the Spline web app.",
        fromfile_prefix_chars='@',
    )
    parser.add_argument('bind', metavar='bind', nargs='?', type=parse_bind,
                        help='what to bind to, either host:port or unix://path')
    parser.add_argument('--dev', action='store_true', dest='spline.debug',
                        help='run in development mode')
    parser.add_argument('--db', metavar='database-url', dest='sqlalchemy.url',
                        help='SQLAlchemy-style URL to your database')

    # TODO this could totally be in the db or wherever as long as the app can
    # restart itself after changing it
    parser.add_argument('-P', '--plugin', action='append', dest='spline.plugins',
                        help='one or more plugins to load, in the form `name:path`')
    parser.add_argument('--data-dir', required=True, dest='spline.datadir',
                        help='directory for storing a pile of disk-backed data')

    # TODO this should /definitely/ be db-backed lol
    parser.add_argument('--site-title', default='spline', dest='spline.site_title',
                        help='name of your website')

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    app = spline.app.main(args)
    if args.bind:
        waitress.serve(app, **args.bind)
    else:
        return app


if __name__ == '__main__':
    application = main()
