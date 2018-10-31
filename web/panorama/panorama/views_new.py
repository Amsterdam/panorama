# Packages
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers as rest_serializers

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


class PanoramaFilter(FilterSet):
    """
    TODO: add documentation
    """

    MAX_RADIUS = 250 # meters

    radius = filters.NumberFilter(method='radius_filter', label='Radius')
    newest_in_radius = filters.BooleanFilter(method='newest_in_radius_filter', label='Only return newest in radius')

    timestamp = filters.DateTimeFromToRangeFilter(label='Timestamp', widget=widgets.DateRangeWidget())

    # TODO: should be add a year filter?
    # year = filters.NumberFilter(method='year_filter', label='Year')

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

    def get_radius_query(self, queryset, value):
        if not self.is_filter_enabled('x') or not self.is_filter_enabled('y'):
            raise rest_serializers.ValidationError('x and y parameters must be set to use the radius filter')

        try:
            # TODO: use NumberFilters!
            x = float(self.data['x'])
            y = float(self.data['y'])
        except ValueError:
            raise rest_serializers.ValidationError('x and y parameters must be numbers')

        return (
            "ST_DWithin(ST_SetSRID(ST_MakePoint(%s, %s), 28992), _geolocation_2d_rd, %s)",
            [x, y, value]
        )

    def get_bbox_query(self, queryset, value):
        coordinates = value.split(',')

        if len(coordinates) != 4:
            raise rest_serializers.ValidationError('a bbox consists of 4 numbers')

        try:
            coordinates = list(map(lambda coordinate: float(coordinate), coordinates))
        except ValueError:
            raise rest_serializers.ValidationError('bbox coordinates must be numbers')

        return (
            "_geolocation_2d_rd && ST_MakeEnvelope(%s, %s, %s, %s)",
            coordinates
        )


    def is_filter_enabled(self, filter):
        return filter in self.data and self.data[filter]

    def radius_filter(self, queryset, name, value):
        if self.is_filter_enabled('bbox'):
            raise rest_serializers.ValidationError('radius and bbox filters are mutually exclusive')

        if value > self.MAX_RADIUS:
            raise rest_serializers.ValidationError('radius can be at most %s meters' % MAX_RADIUS)

        (radius_where, radius_params) = self.get_radius_query(queryset, value)

        queryset = queryset.extra(
            where=[
                radius_where
            ],
            params=radius_params
        )

        return queryset


    def newest_in_radius_filter(self, queryset, name, value):
        if not (self.is_filter_enabled('bbox') or self.is_filter_enabled('radius')):
            raise rest_serializers.ValidationError('bbox or radius filter must be enabled to use newest in radius')

        # TODO: check area < MAXIMUM_AREA
        # area = compute_area()

        # TODO: get radius from mission type
        newest_in_radius_radius = 5

        # TODO: explain
        if self.is_filter_enabled('radius'):
            (extra_geom_where, extra_geom_params) = self.get_radius_query(queryset, self.data['radius'])
        elif self.is_filter_enabled('bbox'):
            (extra_geom_where, extra_geom_params) = self.get_bbox_query(queryset, self.data['bbox'])
        else:
            extra_geom_where = 'true'
            extra_geom_params = []


        return queryset.extra(
            where=[
                """NOT EXISTS (
                    SELECT *
                    FROM panoramas_panorama newer
                    WHERE
                        newer.timestamp > timestamp AND
                        ST_DWithin(newer._geolocation_2d_rd, _geolocation_2d_rd, %s) AND
                        {0}
                )""".format(extra_geom_where)
            ],
            params=([newest_in_radius_radius] + extra_geom_params)
        )


    def bbox_filter(self, queryset, name, value):
        if self.is_filter_enabled('radius'):
            raise rest_serializers.ValidationError('radius and bbox filters are mutually exclusive')

        (bbox_where, bbox_params) = self.get_bbox_query(queryset, value)

        queryset = queryset.extra(
            where=[
                bbox_where
            ],
            params=bbox_params
        )

        return queryset


class PanoramaFilterAdjacent(PanoramaFilter):

    DEFAULT_ADJACENT_RADIUS = 20

    def __init__(self, data=None, queryset=None, request=None, prefix=None):
        if not ('radius' in data and data['radius']):
            data = request.GET.copy()
            data['radius'] = self.DEFAULT_ADJACENT_RADIUS

        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)


    def get_radius_query(self, queryset, value):
        return (
            "ST_DWithin(from_geolocation_2d_rd, _geolocation_2d_rd, %s)",
            [value]
        )


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

        filter = PanoramaFilterAdjacent(request=request, queryset=queryset, data=request.query_params)

        if filter.is_filter_enabled('bbox'):
            raise rest_serializers.ValidationError('bbox filter not allowed for adjacent panoramas')

        queryset = filter.qs

        queryset = queryset.extra(order_by=['relative_distance'])

        serializer = AdjacentPanoSerializer(instance=queryset, many=True, context={'request': request})
        return Response(serializer.data)
