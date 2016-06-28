# Packages
from rest_framework import serializers
from rest_framework_gis import fields
# Project
from datasets.panoramas import models


class PanoSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='img_url')
    geometrie = fields.GeometryField(source='geolocation')

    class Meta:
        model = models.Panorama
        exclude = ('path','geolocation',)

