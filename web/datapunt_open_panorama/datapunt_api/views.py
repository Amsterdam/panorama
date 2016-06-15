# Packages
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
# Project
from datasets.panoramas.mixins import ViewLocationMixin, DateConversionMixin
from datasets.panoramas.models import Panorama
from datasets.panoramas.serializers import PanoSerializer


class PanoViewSet(ViewLocationMixin, DateConversionMixin, viewsets.ModelViewSet):
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
            queryset = Panorama.objects.distance(pnt)
            # Checking for range limit
            if 'radius' in request.query_params:
                max_range = request.query_params['radius']
                # Making sure radius is a positive int
                if max_range.isdigit():
                    max_range = int(max_range)
                    queryset = queryset.filter(geolocation__distance_lte=(pnt, D(m=max_range)))
            # Checking for time limits
            if 'vanaf' in request.query_params:
                start_date = self._convert_to_date(request.query_params['vanaf'])
                if start_date:
                    queryset = queryset.filter(timestamp__gte=start_date)
            if 'tot' in request.query_params:
                end_date = self._convert_to_date(request.query_params['tot'])
                if end_date:
                    queryset = queryset.filter(timestamp__lt=end_date)
            # Finishing up
            try:
                pano = queryset.order_by('distance')[0]
                pano = PanoSerializer(pano, context={'request': request}).data
            except IndexError:
                # No results were found
                pano = []
        else:
            pano = {'error': 'Geen coordinaten gevonden'}
        return Response(pano)

    def retrieve(self, request, pk=None):
        pano = get_object_or_404(Panorama, pano_id=pk)
        resp = PanoSerializer(pano, context={'request': request})
        return Response(resp.data)


