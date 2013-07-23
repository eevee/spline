from __future__ import division
from __future__ import unicode_literals

def format_datetime(dt):
    return dt.strftime("%a %b %d, %Y @ %H:%M")


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
