import logging
# Packages
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework_gis import fields
# Project
from datasets.panoramas import models
from datapunt_api.datapunt_rest import LinksField, HALSerializer

log = logging.getLogger(__name__)

MAX_ADJACENCY = 21


class AdjacencySerializer(serializers.ModelSerializer):
    pano_id = serializers.ReadOnlyField(source='to_pano.pano_id')
    direction = serializers.DecimalField(max_digits=20, decimal_places=2)
    angle = serializers.DecimalField(max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(max_digits=20, decimal_places=2)
    distance = serializers.DecimalField(max_digits=20, decimal_places=2)
    year = serializers.IntegerField(source='to_year')

    class Meta:
        model = models.Adjacency
        fields = ('pano_id', 'direction', 'angle', 'heading', 'pitch', 'distance', 'year',)


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

    class Meta:
        model = models.Panorama
        exclude = ('path', 'geolocation', 'adjacent_panos', '_geolocation_2d',
                   '_geolocation_2d_rd', 'status', 'status_changed')

    def to_representation(self, instance):
        return super().to_representation(instance)

    def get_image_sets(self, instance):
        serializer = ImageLinksSerializer(instance=instance, context={'request': self.context['request']})
        return serializer.data


class FilteredPanoSerializer(PanoSerializer):
    adjacent = serializers.SerializerMethodField(source='get_adjacent')

    class Models:
        adjacency_model = models.Adjacency
        panorama_model = models.Panorama
        adjacency_serializer = AdjacencySerializer

    def __init__(self, instance=None, data=empty, filter_dict={}, **kwargs):
        self.filter = filter_dict
        super().__init__(instance, data, **kwargs)

    def get_adjacent(self, instance):
        qs = self.Models.adjacency_model.objects.filter(
            from_pano=instance,
            distance__lt=MAX_ADJACENCY,
            to_pano__status=self.Models.panorama_model.STATUS.done
        )
        if 'vanaf' in self.filter:
            qs = qs.exclude(to_pano__timestamp__lt=self.filter['vanaf'])
        if 'tot' in self.filter:
            qs = qs.exclude(to_pano__timestamp__gt=self.filter['tot'])

        serializer = self.Models.adjacency_serializer(instance=qs, many=True)
        return serializer.data

