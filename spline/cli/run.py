"""Entry point for running a spline instance as a web app."""
# NOTE: this code CANNOT EVER go in spline/app.py; running that directly will
# change its name to __main__ which will make pyramid confused and unhappy.
import argparse

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


def configure_parser(subparser):
    p_run = subparser.add_parser('run')
    p_run.set_defaults(func=serve_app)
    p_run.add_argument(
        '--dev', action='store_true', dest='spline.debug',
        help="run in development mode")
    p_run.add_argument(
        '--data-dir', required=True, dest='spline.datadir',
        help="directory for storing uploaded files and other disk-backed data")
    p_run.add_argument(
        'bind', metavar='bind', nargs='?', type=parse_bind,
        help="address to bind to, either host:port or unix://path")

    # TODO this should /definitely/ be db-backed lol
    p_run.add_argument(
        '--site-title', default='spline', dest='spline.site_title',
        help="name of your website")


def serve_app(parser, args):
    app = spline.app.main({}, **vars(args))
    if args.bind:
        import waitress
        waitress.serve(app, **args.bind)
    else:
        # TODO this is for playing nicely with uwsgi's paste-serve, but will
        # just quietly exit if you run directly as CLI, oops?
        return app
