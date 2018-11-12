# Packages
import math
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers as rest_serializers

from django.db.models import Q, Exists, OuterRef, Func, F, Expression, Value

from django.db import models
from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.geos import Polygon

from django_filters.rest_framework.filterset import FilterSet
from django_filters.rest_framework import filters
from django_filters import widgets, fields
from django_filters.rest_framework import DjangoFilterBackend

# Project
from datapunt_api import rest

from datasets.panoramas.models_new import PanoramaNew, AdjacencyNew
from datasets.panoramas.serializers_new import PanoSerializerNew, FilteredPanoSerializerNew, AdjacentPanoSerializer


MISSION_TYPE_CHOICES = (
    ('bi', 'bi'),
    ('woz', 'woz')
)

# https://stackoverflow.com/questions/47094982/django-subquery-and-annotations-with-outerref
class RawCol(Expression):

    def __init__(self, model, field_name, output_field=None):
        field = model._meta.get_field(field_name)
        self.table = model._meta.db_table
        self.column = field.column
        super().__init__(output_field=output_field)

    def as_sql(self, compiler, connection):
        sql = f'"{self.table}"."{self.column}"'
        return sql, []

class PanoramaFilter(FilterSet):
    """
    TODO: add documentation
    """

    MAX_RADIUS = 1000 # meters

    # the size of a map tile on https://data.amsterdam.nl/ on zoom
    # level 11 is approximately 500 square meters.
    # Panorama photos are displayed on zoom level 11 and up.
    MAX_NEWEST_IN_RANGE_RADIUS = 250 # meters

    # TODO: for now, both filters only accept RD:28992 coordinates
    bbox = filters.CharFilter(method='bbox_filter', label='Bounding box')
    radius = filters.NumberFilter(method='radius_filter', label='Radius')

    newest_in_range = filters.BooleanFilter(method='newest_in_range_filter', label='Only return newest in range')

    timestamp = filters.DateTimeFromToRangeFilter(label='Timestamp', widget=widgets.DateRangeWidget())

    # TODO: should we add a year filter, for convenience?
    # year = filters.NumberFilter(method='year_filter', label='Year')

    mission_type = filters.ChoiceFilter(choices=MISSION_TYPE_CHOICES)

    class Meta(object):
        model = PanoramaNew

        fields = (
            'timestamp',
            'newest_in_range',
            'radius',
            'bbox',
            'mission_type'

            # TODO: add lat, lon
            # TODO: add x, y
        )

    def get_radius_query(self, queryset, value):
        if not self.is_filter_enabled('x') or not self.is_filter_enabled('y'):
            raise rest_serializers.ValidationError('x and y parameters must be set to use the radius filter')

        try:
            # TODO: use NumberFilters!
            x = float(self.data['x'])
            y = float(self.data['y'])
        except ValueError:
            raise rest_serializers.ValidationError('x and y parameters must be numbers')

        point = Func(Value(x), Value(y), function='ST_MakePoint', output_field=GeometryField())
        srid_point = Func(point, 28992, function='ST_SetSRID', output_field=GeometryField())

        return queryset \
            .annotate(within=Func(srid_point, F('_geolocation_2d_rd'), \
                Value(value), function='ST_DWithin', output_field=models.BooleanField())) \
            .filter(within=True)

    def bbox_from_string(self, value):
        try:
            coordinates = list(map(lambda coordinate: float(coordinate), value.split(',')))
        except ValueError:
            raise ValueError('bbox coordinates must be numbers')

        if len(coordinates) != 4:
            raise ValueError('a bbox consists of 4 numbers')

        return {
            'x1': coordinates[0],
            'y1': coordinates[1],
            'x2': coordinates[2],
            'y2': coordinates[3]
        }

    def get_bbox_query(self, queryset, value):
        try:
            bbox = self.bbox_from_string(value)
        except ValueError as e:
            rest_serializers.ValidationError(str(e))

        bbox_sql = Func(Value(bbox['x1']), Value(bbox['y1']), \
            Value(bbox['x2']), Value(bbox['y2']), 28992, \
            function='ST_MakeEnvelope', output_field=GeometryField())

        return queryset \
            .filter(_geolocation_2d_rd__bboverlaps=(bbox_sql))


    def is_filter_enabled(self, filter):
        return filter in self.data and self.data[filter]

    def radius_filter(self, queryset, name, value):
        if self.is_filter_enabled('bbox'):
            raise rest_serializers.ValidationError('radius and bbox filters are mutually exclusive')

        if value > self.MAX_RADIUS:
            raise rest_serializers.ValidationError('radius can be at most %s meters' % self.MAX_RADIUS)

        return self.get_radius_query(queryset, value)


    def get_skip_not_exists(self):
        return None

    def newest_in_range_filter(self, queryset, name, value):
        if not (self.is_filter_enabled('bbox') or self.is_filter_enabled('radius')):
            raise rest_serializers.ValidationError('bbox or radius filter must be enabled to use newest in radius')

        # TODO: get radius from mission type
        newest_in_range_radius = 5

        exists = queryset.model.objects \
            .values('id') \
            .filter(timestamp__gt=OuterRef('timestamp')) \
            .annotate(within=Func(RawCol(queryset.model, '_geolocation_2d_rd'), F('_geolocation_2d_rd'), \
                Value(newest_in_range_radius), function='ST_DWithin', output_field=models.BooleanField())) \
            .filter(within=True)

        # The exists subquery which selects panoramas only if they are the newest
        # within a range of meters performs much faster if we include the radius or
        # bounding box filter from the outer query:
        if self.is_filter_enabled('radius'):
            try:
                radius = float(self.data['radius'])
            except ValueError:
                raise rest_serializers.ValidationError('radius parameter must be a number')

            if radius > self.MAX_NEWEST_IN_RANGE_RADIUS:
                raise rest_serializers.ValidationError('radius for newest_in_range filter can be at most %s meters' % self.MAX_NEWEST_IN_RANGE_RADIUS)

            # TODO: add padding radius with newest_in_range radius
            exists = self.get_radius_query(exists, radius)
        elif self.is_filter_enabled('bbox'):
            # Square that fits circle with radius = MAX_NEWEST_IN_RANGE_RADIUS
            # has area of:
            max_area = math.pow(self.MAX_NEWEST_IN_RANGE_RADIUS * 2, 2)

            bbox_string = self.data['bbox']

            try:
                bbox = self.bbox_from_string(bbox_string)
            except ValueError as e:
                rest_serializers.ValidationError(str(e))

            area = abs(bbox['x2'] - bbox['x1']) * abs(bbox['y2'] - bbox['y1'])

            if area > max_area:
                raise rest_serializers.ValidationError('area for newest_in_range filter can be at most %s square meters' % max_area)

            exists = self.get_bbox_query(exists, bbox_string)

        not_exists_filter = Q(not_exists=True)

        if self.get_skip_not_exists():
            not_exists_filter = self.get_skip_not_exists() | not_exists_filter

        return queryset.annotate(
            not_exists=~Exists(exists, output_field=models.BooleanField())
        ).filter(not_exists_filter)


    def bbox_filter(self, queryset, name, value):
        if self.is_filter_enabled('radius'):
            raise rest_serializers.ValidationError('radius and bbox filters are mutually exclusive')

        return self.get_bbox_query(queryset, value)


class PanoramaFilterAdjacent(PanoramaFilter):

    DEFAULT_ADJACENT_RADIUS = 20

    def __init__(self, data=None, queryset=None, request=None, prefix=None, pano_id=None):
        self.pano_id = pano_id

        if not ('radius' in data and data['radius']):
            data = request.GET.copy()
            data['radius'] = self.DEFAULT_ADJACENT_RADIUS

        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

    def get_skip_not_exists(self):
        if self.pano_id:
            return Q(pano_id=self.pano_id)

        return super().get_skip_not_exists()


    def get_radius_query(self, queryset, value):
        return queryset \
            .annotate(within=Func(F('from_geolocation_2d_rd'), F('_geolocation_2d_rd'), \
                Value(value), function='ST_DWithin', output_field=models.BooleanField())) \
            .filter(within=True)


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

    filter_backends = (DjangoFilterBackend,)
    filter_class = PanoramaFilter

    @action(detail=True)
    def adjacent(self, request, pano_id):
        queryset = AdjacencyNew.objects.filter(from_pano_id=pano_id)

        filter = PanoramaFilterAdjacent(request=request, queryset=queryset, data=request.query_params, pano_id=pano_id)

        if filter.is_filter_enabled('bbox'):
            raise rest_serializers.ValidationError('bbox filter not allowed for adjacent panoramas')

        queryset = filter.qs

        queryset = queryset.extra(order_by=['relative_distance'])

        serializer = AdjacentPanoSerializer(instance=queryset, many=True, context={'request': request})
        return Response(serializer.data)
