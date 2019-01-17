import logging
from collections import OrderedDict
# Packages
from django.db.models import BooleanField
from django.db.models import Q, Exists, OuterRef, Func, F, Value

from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework_gis import fields
# Project
from datasets.panoramas import models, models_new
from datapunt_api.rest import LinksField, HALSerializer

from panorama.views_new import RawCol

log = logging.getLogger(__name__)

MAX_ADJACENCY = 21
MAX_MISSION_DISTANCE = 10
MISSION_DISTANCE_MARGIN = 0.7


class AdjacencySerializer(serializers.ModelSerializer):
    pano_id = serializers.ReadOnlyField()
    direction = serializers.SerializerMethodField(source='get_direction')
    angle = serializers.SerializerMethodField(source='get_angle')
    heading = serializers.DecimalField(source='relative_heading', max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(source='relative_pitch', max_digits=20, decimal_places=2)
    distance = serializers.DecimalField(source='relative_distance', max_digits=20, decimal_places=2)
    year = serializers.IntegerField(source='mission_year')

    class Meta:
        model = models_new.Adjacencies
        fields = ('pano_id', 'direction', 'angle', 'heading', 'pitch', 'distance', 'year',)

    def get_direction(self, instance):
        "Unused - meaningless parameter, forcefully set to null"
        return None

    def get_angle(self, instance):
        "Unused - meaningless parameter, forcefully set to null"
        return None


class ImageLinksSerializer(serializers.ModelSerializer):
    equirectangular = serializers.ReadOnlyField(source='equirectangular_img_urls')
    cubic = serializers.ReadOnlyField(source='cubic_img_urls')
    thumbnail = serializers.HyperlinkedIdentityField(view_name='thumbnail-detail',
                                                     lookup_field='pano_id',
                                                     format='html')

    class Meta:
        model = models.Panorama
        fields = ('equirectangular', 'thumbnail', 'cubic')


class ThumbnailSerializer(serializers.ModelSerializer):
    heading = serializers.DecimalField(max_digits=20, decimal_places=2)
    pano_id = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField()

    class Meta:
        model = models.Panorama
        fields = ('url', 'heading', 'pano_id')


class PanoLinksField(LinksField):
    lookup_field = 'pano_id'


class PanoSerializer(HALSerializer):
    serializer_url_field = PanoLinksField
    image_sets = serializers.SerializerMethodField(source='get_image_sets')
    geometrie = fields.GeometryField(source='geolocation')
    roll = serializers.DecimalField(max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(max_digits=20, decimal_places=2)
    heading = serializers.DecimalField(max_digits=20, decimal_places=2)
    mission_type = serializers.CharField(source='surface_type')

    class Meta:
        model = models.Panorama
        exclude = ('path', 'geolocation', '_geolocation_2d',
                   '_geolocation_2d_rd', 'status', 'status_changed', 'mission_year',
                   'mission_distance', 'surface_type')

    def to_representation(self, instance):
        return super().to_representation(instance)

    def get_image_sets(self, instance):
        serializer = ImageLinksSerializer(instance=instance, context={'request': self.context['request']})
        return serializer.data


class RecentPanoLinksField(PanoLinksField):
    def to_representation(self, value):
        request = self.context.get('request')
        modified_view_name = self.view_name.replace('recentpanorama', f"recentpanorama-alle")
        return OrderedDict([
            ('self', dict(href=self.get_url(value, modified_view_name, request, None))),
        ])


class RecentPanoSerializer(PanoSerializer):
    serializer_url_field = RecentPanoLinksField

    class Meta(PanoSerializer.Meta):
        model = models.RecentPanorama


class PanoDetailSerializer(PanoSerializer):
    adjacent = serializers.SerializerMethodField(source='get_adjacent')

    def __init__(self, instance=None, data=empty, filter_dict={}, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.filter = filter_dict

    def _filter_recent(self, queryset):
        return queryset

    def get_adjacent(self, instance):
        qs = models_new.Adjacencies.objects.filter(
            Q(from_pano_id=instance.pano_id),
            ~Q(pano_id=instance.pano_id)
        )

        if 'vanaf' in self.filter:
            qs = qs.exclude(timestamp__lt=self.filter['vanaf'])
        if 'tot' in self.filter:
            qs = qs.exclude(timestamp__gt=self.filter['tot'])

        qs = self._filter_recent(qs)
        qs = qs.annotate(within=Func(F('from_geolocation_2d_rd'), F('_geolocation_2d_rd'), Value(MAX_ADJACENCY),
                                     function='ST_DWithin', output_field=BooleanField())).filter(within=True)

        qs = qs.order_by('relative_distance')

        serializer = AdjacencySerializer(instance=qs, many=True)
        return serializer.data


class RecentPanoDetailSerializer(PanoDetailSerializer):
    def _filter_recent(self, queryset):
        exists = models.RecentPanorama.objects.filter(pano_id=OuterRef('pano_id'))
        return queryset.annotate(adjacent=Exists(exists)).filter(adjacent=True)
