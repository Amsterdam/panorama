# Packages
from django.shortcuts import get_object_or_404

from rest_framework.response import Response

# from rest_framework import viewsets
# Project

from datasets.panoramas.mixins import ViewLocationMixin, DateConversionMixin
from datasets.panoramas.models import Panorama
from datasets.panoramas import serializers

from . import datapunt_rest


class PanoramaViewSet(
        datapunt_rest.AtlasViewSet,
        ViewLocationMixin, DateConversionMixin):

    """
    View to retrieve panoramas

    Parameters:

        lat/lon for wgs84 coords
        x/y for RD coords,

    Optional Parameters:

        radius: (int) denoting search radius in meters
        vanaf and/or tot: Several valued are allowed:
            - (int) timestamp
            - (int) year
            - (string) ISO date format yyyy-mm-dd.
            - (string) Eu date formate dd-mm-yyyy.
            if 'vanaf' and 'tot' are given, tot >= vanaf
    """
    queryset = Panorama.objects.all()
    serializer_detail_class = serializers.PanoSerializer
    serializer_class = serializers.PanoSerializer

    def list(self, request):
        """
        Overloading the list view to enable in finding
        the closest pano based on position and possibly distance/time
        """
        pano = []
        # Make sure a position is given, otherwise there is
        # nothing to work with
        coords = self._get_request_coord(request.query_params)
        if not coords:
            return super().list(self, request)

        adjacent_filter, queryset = self._get_filter_and_queryset(coords, request)

        try:
            pano = serializers.FilteredPanoSerializer(
                queryset[0], filter=adjacent_filter,
                context={'request': request}).data
        except IndexError:
            # No results were found
            return Response([])

        return Response(pano)

    def _get_filter_and_queryset(self, coords, request):
        queryset = Panorama.objects.extra(
            select={
                'distance': " geolocation <-> 'SRID=4326;POINT(%s %s)' "},
            select_params=[coords[0], coords[1]])
        max_range = int(request.query_params.get('radius', 20))
        queryset = queryset.extra(
            where=[""" ST_DWithin(ST_GeogFromText('SRID=4326;POINT(%s %s)'),
                   geography(geolocation), %s) """],
            params=[coords[0], coords[1], max_range])
        adjacent_filter = {}
        if 'vanaf' in request.query_params:
            start_date = self._convert_to_date(
                request.query_params['vanaf'])
            if start_date:
                adjacent_filter['vanaf'] = start_date
                queryset = queryset.filter(timestamp__gte=start_date)
        if 'tot' in request.query_params:
            end_date = self._convert_to_date(request.query_params['tot'])
            if end_date:
                adjacent_filter['tot'] = end_date
                queryset = queryset.filter(timestamp__lt=end_date)
        queryset = queryset.extra(order_by=['distance'])
        return adjacent_filter, queryset

    def retrieve(self, request, pk=None):
        pano = get_object_or_404(Panorama, pano_id=pk)
        resp = serializers.FilteredPanoSerializer(pano, context={'request': request})
        return Response(resp.data)
