# Packages
from rest_framework import serializers
# Project
from datasets.panoramas import models

class PanoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Panorama

