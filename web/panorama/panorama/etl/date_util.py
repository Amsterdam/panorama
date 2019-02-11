"""Conversion between GPS and UTC time

    https://confluence.qps.nl/qinsy/en/utc-to-gps-time-correction-32245263.html

Will work for dates after 2015-07-01 (earliest panoramas are in 2016
"""

from datetime import datetime, timezone

# For dates after 2015-07-01
UTC_FROM_GPS = 315964800 - 17
LEAP_SECONDS_INTRODUCED = [1483228800]


def _convert_gps_time(gps_time):
    """Converts the GPS time to unix timestamp, correcting for GPS offset, and leap seconds
    Will work correctly for dates after 2015 - 07 - 01 when the 17th leap second has been
    introduced

    When new leap seconds are introduces, their UTC timestamp need to be added to the constant
    LEAP_SECONDS_INTRODUCED list

    :param gps_time: gps time as timestamp
    :return: unix timestamp representing the date and time, in utc
    """
    gps_time = float(gps_time)
    utc_time = gps_time + UTC_FROM_GPS

    for leap_second_introduced in LEAP_SECONDS_INTRODUCED:
        if utc_time > leap_second_introduced:
            utc_time = utc_time - 1

    return datetime.fromtimestamp(utc_time, tz=timezone.utc)
