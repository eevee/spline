from __future__ import absolute_import

from datetime import datetime
import logging
import sys
import traceback

from colorama import Fore, Back, Style
from colorama.ansitowin32 import AnsiToWin32


class MaybeColoredStreamHandler(logging.StreamHandler):
    """..."""

    def __init__(self, *args, **kwargs):
        super(MaybeColoredStreamHandler, self).__init__(*args, **kwargs)

        try:
            isatty = self.stream.isatty()
        except AttributeError:
            isatty = False

        if isatty:
            self.stream = AnsiToWin32(self.stream, autoreset=True)
        else:
            # Despite the name, AnsiToWin32 is useful for stripping color codes
            # altogether, too
            self.stream = AnsiToWin32(self.stream, strip=True, convert=False)


class StrFormatFormatter(object):
    """Similar to logging.Formatter, but using new-style str.format rather than
    the modulo operator.

    Because str.format is awesome, the `asctime` key and `datefmt` argument are
    gone; instead, you can just use a date format string directly with the
    `created` key (which is a `datetime` rather than a number of seconds),
    e.g.:

        "[{created:%b %d @ %H:%M:%S.%f}] {message}"

    All other LogRecord attributes (except the ones documented as unnecessary)
    are available as keyword arguments.  If you want to use a custom attribute,
    the LogRecord itself is available as the first positional argument:

        "{.custom_attribute} {message}"
    """

    def __init__(self, fmt='{.message}'):
        self.fmt = fmt

    def format(self, record):
        record_dict = self.record_to_dict(record)
        return self.fmt.format(record, **record_dict)

    def record_to_dict(self, record):
        # The stdlib actually steals from record.__dict__ which is totes gross;
        # let's just build a dict manually
        return dict(
            # TODO time zone?  utc?
            created=datetime.fromtimestamp(record.created),
            filename=record.filename,
            funcName=record.funcName,
            levelname=record.levelname,
            levelno=record.levelno,
            lineno=record.lineno,
            module=record.module,
            message=record.getMessage(),
            name=record.name,
            pathname=record.pathname,
            process=record.process,
            processName=record.processName,
            relativeCreated=record.relativeCreated,
            thread=record.thread,
            threadName=record.threadName,
        )

    def formatException(self, exc_info):
        return traceback.format_exception(*exc_info)


class ColorString(object):
    def __init__(self, start, middle, end):
        self.start = start
        self.middle = middle
        self.end = end

    def __format__(self, fmt):
        return self.start + self.middle.__format__(fmt) + self.end


class ColorFormatter(StrFormatFormatter):
    def __init__(self, *args, **kwargs):
        super(ColorFormatter, self).__init__(*args, **kwargs)

        self.level_colors = dict()
        self.record_colors = dict()

    # TODO maybe some reasonable defaults
    def set_level_colors(self, **kwargs):
        self.level_colors.update(kwargs)

    def set_colors(self, **kwargs):
        self.record_colors.update(kwargs)

    # TODO optional parts, like threads, handled better?
    # TODO default color
    def record_to_dict(self, record):
        d = super(ColorFormatter, self).record_to_dict(record)

        for key, value in list(d.items()):
            d[key] = self.colorize(key, value)

        return d

    def colorize(self, record_key, record_value):
        if record_key == 'levelname':
            start = self.level_colors.get(record_value, '')
        else:
            start = self.record_colors.get(record_key, '')

        return ColorString(start, record_value, Style.RESET_ALL)


def autoconfigure():
    # TODO what if logging is already handled?  i guess that's your problem?
    root = logging.getLogger()

    # Create a nice formatter with some nice defaults
    formatter = ColorFormatter(
        '{created} {levelname:>5s} [{name}][{threadName}] {message}',
    )
    formatter.set_level_colors(
        DEBUG=Fore.BLACK,
        INFO='',
        WARNING=Fore.YELLOW,
        ERROR=Fore.RED,
        CRITICAL=Fore.BLACK + Back.RED,
    )
    formatter.set_colors(
        created=Fore.BLACK,
    )

    # Send to stderr
    # TODO maybe don't always send to stderr
    handler = MaybeColoredStreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root.addHandler(handler)

    # TODO snag warnings too
    # TODO better handle exception tracebacks?

    # OK, cool.  Now deal with levels.
    root.setLevel(logging.INFO)


def includeme(config):
    """Handy Pyramid hook for auto-configuring logging as part of app
    configuration.
    """
    autoconfigure()
