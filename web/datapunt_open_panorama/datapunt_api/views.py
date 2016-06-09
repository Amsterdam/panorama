# Packages
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
# Project
from datasets.panoramas.models import Panorama
from datasets.panoramas.serializers import PanoSerializer


class PanoViewSet(viewsets.ModelViewSet):
    """
    View to retrieve panos
    """
    serializer_class = PanoSerializer
    queryset = Panorama.objects.all()

    def list(self, request):
        """
        Overloading the list view to prevent it from serving a list
        but instead use it as an endpoint to finding the closest pano based
        on position and possibly distance/time
        """
        # Make sure a position is given, otherwise there is
        # nothing to work with
        return Response([])


    def retrieve(self, request, pk=None):
        print(pk)
        pano = get_object_or_404(Panorama, pano_id=pk)
        resp = PanoSerializer(pano)
        return Response(resp.data)

