# Packages
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers as rest_serializers

# Project
from django import forms
from datapunt_api import rest

from datasets.panoramas.models_new import PanoramaNew, AdjacencyNew
from datasets.panoramas.serializers_new import PanoSerializerNew, FilteredPanoSerializerNew, AdjacencySerializerNew

from django.db.models import Q

from django.contrib.gis.geos import Polygon

from .queryparam_utils import get_request_coord, convert_to_date, get_int_value

from django_filters.rest_framework.filterset import FilterSet
from django_filters.rest_framework import filters
from django_filters import widgets, fields
from django_filters.rest_framework import DjangoFilterBackend


from datapunt_api import bbox

import datetime

MISSION_TYPE_CHOICES = (
    ('bi', 'bi'),
    ('woz', 'woz')
)

class PanoramaFilter(FilterSet):
    """
    TODO: add documentation
    """

    MAX_RADIUS = 250 # meters

    radius = filters.NumberFilter(method='radius_filter', label='Radius')
    newest_in_radius = filters.BooleanFilter(method='newest_in_radius_filter', label='Only return newest in radius')

    timestamp = filters.DateTimeFromToRangeFilter(label='Timestamp', widget=widgets.DateRangeWidget())

    bbox = filters.CharFilter(method='bbox_filter', label='Bounding box')
    mission_type = filters.ChoiceFilter(choices=MISSION_TYPE_CHOICES)

    class Meta(object):
        model = PanoramaNew

        fields = (
            'timestamp',
            'newest_in_radius',
            'radius',
            'bbox',
            'mission_type'

            # TODO: add lat, lon
            # TODO: add x, y
        )

    def is_filter_enabled(self, filter):
        return filter in self.request.GET and self.request.GET[filter]

    def radius_filter(self, queryset, name, value):
        if self.is_filter_enabled('bbox'):
            raise rest_serializers.ValidationError('radius and bbox filters are mutually exclusive')

        return queryset


    def newest_in_radius_filter(self, queryset, name, value):
        if not (self.is_filter_enabled('bbox') or self.is_filter_enabled('radius')):
            raise rest_serializers.ValidationError('bbox or radius filter must be enabled to use newest in radius')

        # TODO: check area < MAXIMUM_AREA
        # area = compute_area()

        # TODO: get radius from mission type
        radius = 5

        return queryset.extra(
            where=[
                """NOT EXISTS (
                    SELECT *
                    FROM panoramas_panorama newer
                    WHERE
                        newer.timestamp > panoramas_panorama.timestamp AND
                        ST_DWithin(newer._geolocation_2d_rd, panoramas_panorama._geolocation_2d_rd, %s)
                )"""
            ],
            params=[radius]
        )


    def bbox_filter(self, queryset, name, value):
        if self.is_filter_enabled('radius'):
            raise rest_serializers.ValidationError('radius and bbox filters are mutually exclusive')

        # TODO: read bbox from url params
        polygon = Polygon.from_bbox((119900, 486500, 120000, 487000))

        return queryset.filter(
            Q(**{"_geolocation_2d_rd__bboverlaps": polygon}))


class PanoramaViewSetNew(rest.DatapuntViewSet):
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
    queryset = PanoramaNew.done.all()
    serializer_detail_class = FilteredPanoSerializerNew
    serializer_class = PanoSerializerNew

    filter_class = PanoramaFilter
    filter_backends = (DjangoFilterBackend,)

    @action(detail=True)
    def adjacent(self, request, pano_id):
        queryset = AdjacencyNew.objects.filter(
            from_pano_id=pano_id
        )

        # TODO: create filter for radius
        radius = 22
        queryset = queryset.extra(
            where=[
                "ST_DWithin(from_geolocation_2d_rd, to_geolocation_2d_rd, %s)"
            ],
            params=[radius]
        )

        # TODO: create filter for adjacent newest_in_radius
        queryset = queryset.extra(
            where=[
                """NOT EXISTS (
                    SELECT *
                    FROM panoramas_panorama newer
                    WHERE
                        newer.timestamp > to_timestamp AND
                        ST_DWithin(newer._geolocation_2d_rd, to_geolocation_2d_rd, %s)
                )"""
            ],
            params=[4.3]
        )

        queryset = queryset.extra(order_by=['distance'])

        serializer = AdjacencySerializerNew(instance=queryset, many=True)
        return Response(serializer.data)
