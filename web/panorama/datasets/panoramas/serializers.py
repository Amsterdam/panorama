# Packages
from rest_framework import serializers
# Project
from datasets.panoramas import models


#class PanoSerializer(serializers.ModelSerializer):
class PanoSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='img_url')

    class Meta:
        model = models.Panorama

