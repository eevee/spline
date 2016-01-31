import argparse
import shlex

import spline.cli.database
import spline.cli.run


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


def make_arg_parser(initdb=False):
    parser = ShlexArgumentParser(
        prog='spline',
        description="Run or administrate a Spline web app.",
        fromfile_prefix_chars='@',
    )
    parser.add_argument(
        '--db', metavar='database-url', dest='sqlalchemy.url',
        required=True,
        help='SQLAlchemy-style URL to your database')

    # TODO this could totally be in the db or wherever as long as the app can
    # restart itself after changing it
    parser.add_argument(
        '-P', '--plugin', action='append', dest='spline.plugins',
        help="plugin to load, in the form 'name:mountpoint'; may be given multiple times")

    subp = parser.add_subparsers(title='commands')

    spline.cli.database.configure_parser(subp)
    spline.cli.run.configure_parser(subp)
    parser.add_argument('--comic-name', default='My first comic', dest='spline.comic_name',
                        help='title of your first comic')
    parser.add_argument('--chapter-name', default='My first chapter', dest='spline.chapter_name',
                        help='title of the first chapter of your comic')

    return parser
