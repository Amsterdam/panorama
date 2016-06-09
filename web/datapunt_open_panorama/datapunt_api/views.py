# Packages
from django.contrib.gis.geos import Point
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
        """
        # Make sure a position is given, otherwise there is
        # nothing to work with
        coords = self._get_request_coord(request.query_params)
        return Response([])

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
        if 'lat' in .query_params and 'lon' in query_params:
            lat = query_params['lat']
            lon = query_params['lon']
            # @TODO Doing value sanity check
            coords = (lat, lon)
        elif 'x' in query_params and 'y' in query_params:
            lat = query_params['x']
            lon = query_params['y']
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

