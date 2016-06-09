# Python
import datetime
# Packages
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
# Project
from datasets.panoramas.models import Panorama
from datasets.panoramas.serializers import PanoSerializer


class PanoViewSet(viewsets.ModelViewSet):
    """
    View to retrieve panos
    """
    serializer_class = PanoSerializer
    queryset = Panorama.objects.all()

    def list(self, request):
        """
        Overloading the list view to prevent it from serving a list
        but instead use it as an endpoint to finding the closest pano based
        on position and possibly distance/time

        Required Parameters:
        lat/lon for wgs84 coords or x/y for RD coords, float or int values

        Optional Parameters:
        radius: (int) denoting search radius in meters
        vanaf and/or tot: Several valued are allowed:
            - (int) timestamp
            - (int) year
            - (string) ISO date format yyyy-mm-dd.
            - (string) Eu date formate dd-mm-yyyy.
            if vanaf and tot are given, tot must be bigger then vanaf
        """
        pano = []
        # Make sure a position is given, otherwise there is
        # nothing to work with
        coords = self._get_request_coord(request.query_params)
        if coords:
            # Quering
            pnt = GEOSGeometry(('POINT(%f %f 10)' % (coords[0], coords[1])), srid=4326)
            pano = Panorama.objects.distance(pnt)
            # Checking for range limit
            if 'radius' in request.query_params:
                max_range = int(request.query_params['radius'])
            # Checking for time limits
            if 'vanaf' in request.query_params:
                start_date = self._convert_to_timestamp(request.query_params['vanaf'])
                pano = pano.filter(timestamp__gte=timestamp)
            if 'tot' in request.query_params:
                end_date = self._convert_to_timestamp(request.query_params['tot'])
                pano = pano.filter(timestamp__lt=timestamp)
            # Finishing up
            pano = pano.order_by('distance')[0]
            pano = PanoSerializer(pano)
        else:
            pano = {'error': 'Geen coordinaten gevonden'}
        return Response(pano.data)

    def retrieve(self, request, pk=None):
        pano = get_object_or_404(Panorama, pano_id=pk)
        resp = PanoSerializer(pano)
        return Response(resp.data)

    def _get_request_coord(self, query_params):
        """
        Retrieves the coordinates to work with. It allows for either lat/lon coord,
        for wgs84 or 'x' and 'y' for RD. Just to be on the safe side a value check
        a value check is done to make sure that the values are within the expected
        range. If they seem to be RD values, an attempt is made to convert them
        to wgs84 values
        """
        if 'lat' in query_params and 'lon' in query_params:
            lat = float(query_params['lat'])
            lon = float(query_params['lon'])
            # @TODO Doing value sanity check
            coords = (lat, lon)
        elif 'x' in query_params and 'y' in query_params:
            lat = float(query_params['x'])
            lon = float(query_params['y'])
            # These should be Rd coords, convert to WGS84
            coords = self._convert_coords(lat, lon, 28992, 4326)
        # No good coords found
        else:
            return None
        return coords

    def _convert_coords(self, lat, lon, orig_srid, dest_srid):
        """
        Convertes a point between two coordinates
        Parameters:
        lat - Latitude as float
        lon - Longitude as float
        original_srid - The int value of the point's srid
        dest_srid - The srid of the coordinate system to convert too

        Returns
        The new coordinates as a tuple. None if the convertion failed
        """
        coords = None
        p = Point(lat, lon, srid=original_srid)
        p.transform(dest_srid)
        coords = p.coords
        return coords

    def _convert_to_timestamp(self, input_date):
        """
        Converts input time to a timestamp.
        Allowed input is timestamp, or string denoting a date in ISO or EU format

        Parameters:
        input_date: The input from the query params

        Returns:
        Timestamp as int if conversion is succesful. None otherwise
        """
        timestamp = None
        year = None
        date_format = '%Y-%m-%d'
        # Looking at the length of the input
        if len(input_date) == 4:
            # This will be handled as a year
            timestamp = datetime.datetime.strptime('%s-01-01' % input_date, date_format).timestamp()
        elif '-' in input_date:
            # A date string. Tring to get year, month, dat
            if input_date.find('-') == 2:
                # EU format
                date_format = '%d-%m-%Y'
                timestamp = datetime.datetime.strptime(input_date, date_format).timestamp()
        else:
            # Assume it is aleady a timestamp
            timestamp = input_date
        # Making sure an int is returned
        return int(timestamp)
