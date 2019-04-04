"""
A collection of utils for dealing with query params
"""
# Python
import datetime
# Packages
from django.contrib.gis.geos import Point
from django.utils.datastructures import MultiValueDictKeyError


SRID_WSG84 = 4326
SRID_RD = 28992


def get_request_coord(query_params):
    """
    Retrieves the coordinates to work with. It allows for either lat/lon coord,
    for wgs84 or 'x' and 'y' for RD.

    Parameters:
    query_params - the query parameters dict from which to retrieve the coords

    Returns coordinates in WSG84 longitude,latitude
    """
    if 'lat' in query_params and 'lon' in query_params:
        lon = float(query_params['lon'])
        lat = float(query_params['lat'])
        return lon, lat
    elif 'x' in query_params and 'y' in query_params:
        x = float(query_params['x'])
        y = float(query_params['y'])
        return _convert_coords(x, y, SRID_RD, SRID_WSG84)
    else:
        return None


def _convert_coords(lon, lat, orig_srid, dest_srid):
    """
    Convertes a point between two coordinates
    Parameters:
    lon - Longitude as float
    lat - Latitude as float
    original_srid - The int value of the point's srid
    dest_srid - The srid of the coordinate system to convert too

    Returns
    The new coordinates as a tuple. None if the convertion failed
    """
    p = Point(lon, lat, srid=orig_srid)
    p.transform(dest_srid)
    return p.coords


def convert_to_date(request, param_name):
    """
    Converts input time to a date object.
    Allowed input is timestamp, or string denoting a date in ISO or EU format

    Parameters:
    input_date: The input from the query params

    Returns:
    A python date object
    """
    if param_name not in request.query_params:
        return None

    input_date = request.query_params[param_name]
    date_format = '%Y-%m-%d'  # Assume iso
    if input_date.isdigit():
        # The next test will make it that timestamp from around 3 am on 1-1-1970
        # will be handled as dates. :
        # however this should not be an issue
        if len(input_date) == 4:
            # Only a year is given
            date_format = '%Y'
        else:
            # Treat itas a timestamp
            try:
                date_obj = datetime.date.fromtimestamp(int(input_date))
            except OverflowError:  # Just to be on the safe side, you never know
                date_obj = None
            return date_obj
    elif '-' in input_date:
        # A date string. Determinig format
        if input_date.find('-') == 2:
            # EU format
            date_format = '%d-%m-%Y'
    else:
        # Un-workable input
        return None
    # Attempting to convert the string to a date object
    try:
        date_obj = datetime.datetime.strptime(input_date, date_format).date()
    except ValueError:
        # Cannot convert the input to a date object
        date_obj = None
    return date_obj


def get_int_value(request, param_name, default, lower=0, upper=None, strategy='cutoff'):
    try:
        value = int(request.query_params[param_name])
        if lower is None or lower <= value:
            if upper is None or value <= upper:
                return value
            elif strategy is 'cutoff' and upper is not None:
                return upper
            elif strategy is 'modulo' and upper is not None:
                return value % upper
    except (ValueError, MultiValueDictKeyError):
        pass
    return int(default)


def get_float_value(request, param_name, default, lower=None, upper=None):
    try:
        value = float(request.query_params[param_name])
        if (lower is None or lower <= value) \
                and (upper is None or value <= upper):
            return value
    except (ValueError, MultiValueDictKeyError):
        pass
    return float(default)
