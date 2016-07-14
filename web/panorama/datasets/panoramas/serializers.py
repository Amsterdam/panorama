# Packages
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework_gis import fields
# Project
from datasets.panoramas import models


class AdjacencySerializer(serializers.ModelSerializer):
    pano_id = serializers.ReadOnlyField(source='to_pano.pano_id')
    direction = serializers.DecimalField(max_digits=20, decimal_places=2)
    angle = serializers.DecimalField(max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(max_digits=20, decimal_places=2)
    distance = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = models.Adjacency
        fields = ('pano_id', 'direction', 'angle', 'heading', 'pitch', 'distance',)


class ImageLinksSerializer(serializers.ModelSerializer):
    raw = serializers.ReadOnlyField(source='img_url')
    normalized = serializers.HyperlinkedIdentityField(view_name='normalized-detail', lookup_field='pano_id', format='html')
    thumbnail = serializers.HyperlinkedIdentityField(view_name='thumbnail-detail', lookup_field='pano_id', format='html')

    class Meta:
        model = models.Panorama
        fields = ('raw', 'normalized', 'thumbnail')


class PanoSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(source='get_images')
    geometrie = fields.GeometryField(source='geolocation')
    adjacent = AdjacencySerializer(source='to_adjacency', many=True)
    roll = serializers.DecimalField(max_digits=20, decimal_places=2)
    pitch = serializers.DecimalField(max_digits=20, decimal_places=2)
    heading = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = models.Panorama
        exclude = ('path','geolocation','adjacent_panos','_geolocation_2d')

    def to_representation(self, instance):
        return super().to_representation(instance)

    def get_images(self, instance):
        serializer = ImageLinksSerializer(instance=instance, context={'request': self.context['request']})
        return serializer.data


class FilteredPanoSerializer(PanoSerializer):
    adjacent = serializers.SerializerMethodField(source='get_adjacent')

    def __init__(self, instance=None, data=empty, filter={}, **kwargs):
        self.filter = filter
        super().__init__(instance, data, **kwargs)

    def get_adjacent(self, instance):
        qs = models.Adjacency.objects.filter(from_pano=instance, distance__lt=11)
        if 'vanaf' in self.filter:
            qs = qs.exclude(to_pano__timestamp__lt=self.filter['vanaf'])
        if 'tot' in self.filter:
            qs = qs.exclude(to_pano__timestamp__gt=self.filter['tot'])

        serializer = AdjacencySerializer(instance=qs, many=True)
        return serializer.data
