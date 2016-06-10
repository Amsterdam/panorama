"""
A collection of mixins for different functionalities
"""
# Python
import datetime
# Packages
from django.contrib.gis.geos import Point


class ViewLocationMixin(object):
    """
    A Mixin that adds support for location in handling in the view
    Offers 2 functions:
    _get_requets_coords - retrieve the coords, and possible convert to another
                            coordination system
    _ convert coords - convert coords from one system to another
    """
    def _get_request_coord(self, query_params, convert=4326):
        """
        Retrieves the coordinates to work with. It allows for either lat/lon coord,
        for wgs84 or 'x' and 'y' for RD. Just to be on the safe side a value check
        a value check is done to make sure that the values are within the expected
        range.

        Parameters:
        query_params - the query parameters dict from which to retrieve the coords
        convert - optional parameter. If set an attempt is made to convert to that
                    set
        """
        if 'lat' in query_params and 'lon' in query_params:
            lon = float(query_params['lon'])
            lat = float(query_params['lat'])
            coord_system = 4326
            # @TODO Doing value sanity check
            coords = (lat, lon)
        elif 'x' in query_params and 'y' in query_params:
            lon = float(query_params['x'])
            lat = float(query_params['y'])
            coord_system = 28992
            # Verfing that x is smaller then y
        # No good coords found
        else:
            return None
        if convert and convert != coord_system:
            # These should be Rd coords, convert to WGS84
            coords = self._convert_coords(lat, lon, coord_system, convert)
        print (coords)
        return coords

    def _convert_coords(self, lon, lat, orig_srid, dest_srid):
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
        coords = None
        p = Point(lon, lat, srid=orig_srid)
        p.transform(dest_srid)
        coords = p.coords
        return coords


class DateConversionMixin(object):
    """
    A mixin to help convert a string to a date object
    """
    def _convert_to_date(self, input_date):
        """
        Converts input time to a date object.
        Allowed input is timestamp, or string denoting a date in ISO or EU format

        Parameters:
        input_date: The input from the query params

        Returns:
        A python date object
        """
        date_format = '%Y-%m-%d' # Assume iso
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

