from math import pi, radians, atan2, degrees, log, tan

# Packages
from django.contrib.gis.geos import LineString
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from scipy import misc

from .queryparam_utils import _get_float_value, _get_int_value, _get_request_coord
from datapunt_api.views import PanoramaViewSet
from datasets.panoramas.models import Panorama
from datasets.panoramas.transform.transformer import PanoramaTransformer
from . import datapunt_rest


class ImageViewSet(datapunt_rest.AtlasViewSet):

    """
    View to retrieve normalized images

    Parameters:

        pano_id of Panorama

    """
    lookup_field = 'pano_id'
    queryset = Panorama.objects.all()

    def list(self, request):
        return Response({'error': 'pano_id'})

    def retrieve(self, request, pano_id=None):
        pano = get_object_or_404(Panorama, pano_id=pano_id)
        pt = PanoramaTransformer(pano)
        normalized_pano = pt.get_translated_image(target_width=4000)

        response = HttpResponse(content_type="image/jpeg")
        misc.toimage(normalized_pano).save(response, "JPEG")
        return response


class ThumbnailViewSet(PanoramaViewSet):

    """
    View to retrieve thumbs of a panorama

    Parameters:

        pano_id of Panorama

        or:

        lat/lon for wgs84 coords
        x/y for RD coords,

        in the later case, optional Parameters for finding a panorama:

        radius: (int) denoting search radius in meters (default = 20m)

    Optional Parameters for the thumbnail:

        width: in pixels (max 1600) (default 750)
        angle: in degrees horizontal (max 80), max 20px per degree (default 80)
        horizon: fraction of image that is below horizon (default 0.3)
        heading: direction to look at in degrees (default 0)
        aspect: aspect ratio of thumbnail (width/height, min 1) (default 1.5 (3/2)

    """

    lookup_field = 'pano_id'

    def list(self, request):
        """
        Overloading the list view to enable in finding
        the thumb looking at the given point
        """
        coords = _get_request_coord(request.query_params)
        if not coords:
            return Response({'error': 'pano_id'})

        _, queryset = self._get_filter_and_queryset(coords, request)

        try:
            pano = queryset[0]
            heading = self._get_heading(coords, pano._geolocation_2d)
            line = LineString(coords, pano._geolocation_2d)
            return self.retrieve(request, pano_id=pano.pano_id, target_heading=heading)
        except IndexError:
            # No results were found
            return Response([])

    def _get_heading(self, coords, _geolocation_2d):
        # http://gis.stackexchange.com/questions/29239/calculate-bearing-between-two-decimal-gps-coordinates
        d_lon = radians(_geolocation_2d[0]) - radians(coords[0])

        start_lat = radians(coords[1])
        end_lat =radians(_geolocation_2d[1])
        d_phi = log(tan(end_lat/2.0+pi/4.0)/tan(start_lat/2.0+pi/4.0))

        return degrees(atan2(d_lon, d_phi)) % 360.0

    def retrieve(self, request, pano_id=None, target_heading=0):
        heading = _get_int_value(request, 'heading', default=target_heading, lower=0, upper=360)

        target_width = _get_int_value(request, 'width', default=750, lower=1, upper=1600)
        target_angle = _get_int_value(request, 'angle', default=80, lower=0, upper=80)
        target_width, target_angle = self._max_angle_per_width(target_width, target_angle)

        target_horizon = _get_float_value(request, 'horizon', default=0.3, lower=0.0, upper=1.0)
        target_aspect = _get_float_value(request, 'aspect', default=1.5, lower=1.0)

        pano = get_object_or_404(Panorama, pano_id=pano_id)
        pt = PanoramaTransformer(pano)
        normalized_pano = pt.get_translated_image(target_width=target_width,
                                                  target_angle=target_angle,
                                                  target_horizon=target_horizon,
                                                  target_heading=heading,
                                                  target_aspect=target_aspect)

        response = HttpResponse(content_type="image/jpeg")
        misc.toimage(normalized_pano).save(response, "JPEG")
        return response

    def _max_angle_per_width(self, width, angle):
        """
        source resolution is a little over 22 px / degree viewing angle
        for thumbs we cap this at 20 px / degree viewing angle
        """
        if width/angle > 20:
            return width, round(width/20)
        return width, angle
