import logging
# Packages
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework_gis import fields
# Project
from datasets.panoramas.models_new import PanoramaNew, AdjacencyNew
from datapunt_api.rest import LinksField, HALSerializer

log = logging.getLogger(__name__)

MAX_ADJACENCY = 21


class AdjacencySerializerNew(serializers.ModelSerializer):
    pano_id = serializers.CharField(max_length=37, source='to_pano_id')

    direction = serializers.DecimalField(max_digits=20, decimal_places=2)
    angle = serializers.DecimalField(max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(max_digits=20, decimal_places=2)
    distance = serializers.DecimalField(max_digits=20, decimal_places=2)

    year = serializers.IntegerField(source='to_year')

    # TODO: choose better name!
    current = serializers.SerializerMethodField()

    class Meta:
        model = AdjacencyNew
        fields = ('pano_id', 'direction', 'angle', 'heading', 'pitch', 'distance', 'year', 'current')

    def get_current(self, obj):
        return obj.from_pano_id == obj.to_pano_id


class ImageLinksSerializerNew(serializers.ModelSerializer):
    equirectangular = serializers.ReadOnlyField(source='equirectangular_img_urls')
    cubic = serializers.ReadOnlyField(source='cubic_img_urls')
    thumbnail = serializers.HyperlinkedIdentityField(view_name='thumbnail-detail',
                                                     lookup_field='pano_id',
                                                     format='html')

    class Meta:
        model = PanoramaNew
        fields = ('equirectangular', 'thumbnail', 'cubic')


class ThumbnailSerializerNew(serializers.ModelSerializer):
    heading = serializers.DecimalField(max_digits=20, decimal_places=2)
    pano_id = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField()

    class Meta:
        model = PanoramaNew
        fields = ('url', 'heading', 'pano_id')


class PanoLinksFieldNew(LinksField):
    lookup_field = 'pano_id'


class PanoSerializerNew(HALSerializer):
    serializer_url_field = PanoLinksFieldNew
    image_sets = serializers.SerializerMethodField(source='get_image_sets')
    geometrie = fields.GeometryField(source='geolocation')
    roll = serializers.DecimalField(max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(max_digits=20, decimal_places=2)
    heading = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = PanoramaNew
        exclude = ('path', 'geolocation', '_geolocation_2d',
                   '_geolocation_2d_rd', 'status', 'status_changed')

    def to_representation(self, instance):
        return super().to_representation(instance)

    def get_image_sets(self, instance):
        serializer = ImageLinksSerializerNew(instance=instance, context={'request': self.context['request']})
        return serializer.data


class FilteredPanoSerializerNew(PanoSerializerNew):

    def __init__(self, instance=None, data=empty, filter_dict={}, **kwargs):
        self.filter = filter_dict
        super().__init__(instance, data, **kwargs)
