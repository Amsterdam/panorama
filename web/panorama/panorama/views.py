# Packages
from rest_framework.response import Response

# Project
from datasets.panoramas.v1.models import Panorama, RecentPanorama
from datasets.panoramas.v1 import serializers
from datapunt_api import rest

from .queryparam_utils import get_request_coord, convert_to_date, get_int_value


class PanoramaViewSet(rest.DatapuntViewSet):
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
    lookup_field = 'pano_id'
    queryset = Panorama.done.all()
    serializer_detail_class = serializers.PanoDetailSerializer
    serializer_class = serializers.PanoSerializer

    def list(self, request, *_args, **_kwargs):
        """
        Overloading the list view to enable in finding
        the closest pano based on position and possibly distance/time
        :param **kwargs:
        :param **kwargs:
        """
        pano = []
        # Make sure a position is given, otherwise there is
        # nothing to work with
        coords = get_request_coord(request.query_params)
        if not coords:
            return super().list(request)
        else:
            return self.get_nearest_or_none(request, coords)

    def get_nearest_or_none(self, request, coords):
        adjacent_filter, queryset = self._get_filter_and_queryset(
            coords, request)

        try:
            candidate_pano = queryset[0]
            max_range = get_int_value(request, 'radius', 20)
            if candidate_pano.distance_meters <= max_range:
                pano = self.serializer_detail_class(
                    candidate_pano, filter_dict=adjacent_filter,
                    context={'request': request}).data
                return Response(pano)
        except IndexError:
            pass

        # No results were found
        return Response([], status=200)

    def get_queryset(self, *args, **kwargs):
        _, queryset = self._get_filter_and_queryset_by_date(self.queryset, self.request)
        return queryset

    def _get_filter_and_queryset_by_date(self, queryset, request):
        adjacent_filter = {}
        start_date = convert_to_date(request, 'vanaf')
        if start_date is not None:
            adjacent_filter['vanaf'] = start_date
            queryset = queryset.filter(timestamp__gte=start_date)
        end_date = convert_to_date(request, 'tot')
        if end_date is not None:
            adjacent_filter['tot'] = end_date
            queryset = queryset.filter(timestamp__lt=end_date)
        return adjacent_filter, queryset

    def _get_filter_and_queryset(self, coords, request):
        adjacent_filter, queryset = self._get_filter_and_queryset_by_date(self.queryset, request)

        queryset = queryset.extra(
            select={
                'distance_meters': "ST_Distance(geography(_geolocation_2d), "
                                   "ST_GeogFromText('SRID=4326;POINT(%s %s)')) "
            },
            select_params=[coords[0], coords[1]])
        queryset = queryset.extra(
            select={
                'distance': " _geolocation_2d <-> 'SRID=4326;POINT(%s %s)' "
            },
            select_params=[coords[0], coords[1]])
        queryset = queryset.extra(order_by=['distance'])

        return adjacent_filter, queryset


class RecentPanoramaViewSet(PanoramaViewSet):
    queryset = RecentPanorama.objects.all()
    serializer_class = serializers.RecentPanoSerializer
    serializer_detail_class = serializers.RecentPanoDetailSerializer
