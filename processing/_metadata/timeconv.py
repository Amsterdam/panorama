from typing import Iterator

import pandas as pd


def from_gps_time(it: Iterator[pd.Series]) -> Iterator[pd.Series]:
    """Convert GPS timestamps to datetimes.

    Only valid for timestamps after 2015-07-01. Earlier times will be off by
    a few seconds due to lack of leap seconds.
    """
    # UTC offset for dates after 2015-07-01, including the 17 leap seconds
    # since the GPS epoch (1980).
    UTC_FROM_GPS = 315964800 - 17
    # UTC timestamps of leap seconds after 2015-07-01.
    leap_seconds = sorted([1483228800], reverse=True)

    for t in it:
        t = t + UTC_FROM_GPS
        for leap in leap_seconds:
            t -= (t > leap)
        yield pd.to_datetime(t, unit="s", utc=True)
