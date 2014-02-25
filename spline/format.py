from __future__ import division
from __future__ import unicode_literals

from datetime import datetime
import pytz


def format_datetime(dt):
    return dt.strftime("%a %b %d, %Y @ %H:%M")


def format_date(dt):
    return dt.strftime("%a %b %d, %Y")


def format_relative_date(dt):
    # TODO this doesn't do future dates at all
    td = datetime.now(pytz.utc) - dt.astimezone(pytz.utc)
    if td.days == 0:
        if td.seconds < 30:
            return "just now"

        minutes = int(td.seconds / 60 + 0.5)
        if minutes < 5:
            return "a few minutes ago"
        elif minutes < 55:
            return "{} minutes ago".format(minutes)

        hours = int(minutes / 60 + 0.5)
        if hours == 1:
            return "an hour ago"
        elif hours < 24:
            return "{} hours ago".format(hours)

    # TODO i'd rather say yesterday or names of weekdays than "1 day ago", but
    # that requires knowing the target time zone
    days = td.days + int(td.seconds / (24 * 3600) + 0.5)
    if days == 1:
        return "a day ago"
    elif days < 7:
        return "{} days ago".format(days)

    # For a week or more ago, fall back to a date, but omit the year if
    # possible.  This is kinda like ls rules, I think?
    if days < 90:
        return dt.strftime("%b %d")
    elif days < 365 * 50:
        return dt.strftime("%b %d, ’%y")
    else:
        return dt.strftime("%b %d, %Y")


_BYTE_MAGNITUDES = [
    ('B', 'B'),
    ('kB', 'KiB'),
    ('MB', 'MiB'),
    ('GB', 'GiB'),
    ('TB', 'TiB'),
    ('PB', 'PiB'),
]

def format_filesize(b, si=False):
    if si:
        unit = 1000
    else:
        unit = 1024

    magnitude = 0
    while magnitude < len(_BYTE_MAGNITUDES) - 1 and b > unit * 1.1:
        magnitude += 1
        b /= unit

    si_suffix, iec_suffix = _BYTE_MAGNITUDES[magnitude]
    if si:
        suffix = si_suffix
    else:
        suffix = iec_suffix

    return "{0:.3g} {1}".format(b, suffix)
