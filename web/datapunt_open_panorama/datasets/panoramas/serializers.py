# Packages
from rest_framework import serializers
# Project
from datasets.panoramas import models


# Creaing a link field
class LinkField(serializers.ReadOnlyField):
    """
    For consistency using the same url format as the rest of atlas
    """
    def to_representation(self, value):
        request = self.context.get('request')
        #return 'LINK: ' + value
        return '%s://%s%s' %(request.scheme, request.get_host(), value)

#class PanoSerializer(serializers.ModelSerializer):
class PanoSerializer(serializers.ModelSerializer):
    url = LinkField(source='path')

    class Meta:
        model = models.Panorama

