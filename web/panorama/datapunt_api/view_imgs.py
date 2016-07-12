# Packages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from scipy import misc

from datasets.panoramas.transform.transformer import PanoramaTransformer
from datasets.panoramas.models import Panorama
from datapunt_api.views import PanoramaViewSet
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
        coords = self._get_request_coord(request.query_params)
        if not coords:
            return Response({'error': 'pano_id'})

        _, queryset = self._get_filter_and_queryset(coords, request)

        try:
            pano = queryset[0]
            heading = self._get_heading(coords, pano._geolocation_2d)
            return self.retrieve(request, pano_id=pano.pano_id, target_heading=heading)
        except IndexError:
            # No results were found
            return Response([])

    def _get_heading(self, coords, _geolocation_2d):
        sql = "select 1 as id, degrees(st_azimuth(ST_GeogFromText('SRID=4326;POINT(%s %s)'), ST_GeogFromText('SRID=4326;POINT(%s %s)'))) AS heading "
        simpl = Panorama.objects.raw(sql, [_geolocation_2d[0], _geolocation_2d[1], coords[0], coords[1]])[0]
        return simpl.heading

    def retrieve(self, request, pano_id=None, target_heading=0):
        # default query params
        target_width=750
        target_angle=80
        target_horizon=0.3
        target_aspect=1.5

        if 'width' in request.query_params:
            target_width = self._get_int_value(request.query_params['width'], target_width, 1, 1600)

        if 'angle' in request.query_params:
            target_angle = self._get_int_value(request.query_params['angle'], target_angle, 0, 80)

        target_width, target_angle = self._match_width_angle(target_width, target_angle)

        if 'heading' in request.query_params:
            target_heading = self._get_int_value(request.query_params['heading'], target_heading, 0, 360)

        if 'horizon' in request.query_params:
            target_horizon = self._get_float_value(request.query_params['horizon'], target_horizon, 0.0, 1.0)

        if 'aspect' in request.query_params:
            target_aspect = self._get_float_value(request.query_params['aspect'], target_aspect, lower=1.0)

        pano = get_object_or_404(Panorama, pano_id=pano_id)
        pt = PanoramaTransformer(pano)
        normalized_pano = pt.get_translated_image(target_width=target_width,
                                                  target_angle=target_angle,
                                                  target_horizon=target_horizon,
                                                  target_heading=target_heading,
                                                  target_aspect=target_aspect)

        response = HttpResponse(content_type="image/jpeg")
        misc.toimage(normalized_pano).save(response, "JPEG")
        return response

    def _get_int_value(self, param, default, lower=None, upper=None):
        if param.isdigit() \
                and (not lower or lower <= int(param)) \
                and (not upper or int(param) <= upper):
            return int(param)
        return default

    def _match_width_angle(self, width, angle):
        if width/angle > 20:
            return width, round(width/20)
        return width, angle

    def _get_float_value(self, param, default, lower=None, upper=None):
        try:
            value = float(param)
            if (not lower or lower <= value) \
                    and (not upper or value <= upper):
                return value
        except ValueError:
            return default
        return default
