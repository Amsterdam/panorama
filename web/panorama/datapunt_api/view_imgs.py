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
    queryset = Panorama.objects.all()

    def list(self, request):
        return Response({'error': 'pano_id'})

    def retrieve(self, request, pk=None):
        pano = get_object_or_404(Panorama, pano_id=pk)
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

    Optional Parameters:

        width: in pixels (max 1600) (default 750)
        angle: in degrees horizontal (max 80), max 20px per degree (default 80)
        horizon: fraction of image that is below horizon (default 0.3)
        heading: direction to look at in degrees (default 0)
        aspect: aspect ratio of thumbnail (width/height, min. 1) (default 4/3)

    """

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
            heading = self._get_heading(coords, pano.geopoint)
            return self.retrieve(request, pk=pano.pano_id, target_heading=heading)
        except IndexError:
            # No results were found
            return Response([])


    def retrieve(self, request, pk=None, target_heading=0):
        # default query params
        target_width=750
        target_angle=80
        target_horizon=0.3
        target_aspect=4/3

        if 'width' in request.query_params:
            target_width = self._get_thumb_width(request, target_width)

        if 'angle' in request.query_params:
            target_angle = self._get_thumb_angle(request, target_angle)

        target_width, target_angle = self._match_width_angle(target_width, target_angle)

        if 'heading' in request.query_params:
            target_heading = self._get_thumb_heading(request, target_heading)

        if 'horizon' in request.query_params:
            target_horizon = self._get_thumb_horizon(request, target_horizon)

        if 'aspect' in request.query_params:
            target_aspect = self._get_thumb_aspect(request, target_aspect)

        pano = get_object_or_404(Panorama, pano_id=pk)
        pt = PanoramaTransformer(pano)
        normalized_pano = pt.get_translated_image(target_width=target_width,
                                                  target_angle=target_angle,
                                                  target_horizon=target_horizon,
                                                  target_heading=target_heading,
                                                  target_aspect=target_aspect)

        response = HttpResponse(content_type="image/jpeg")
        misc.toimage(normalized_pano).save(response, "JPEG")
        return response

    def _get_thumb_width(self, request, default):
        width = request.query_params['width']
        if width.isdigit() and 0 < int(width) < 1601:
            return int(width)
        return default

    def _get_thumb_angle(self, request, default):
        angle = request.query_params['angle']
        if angle.isdigit() and 0 <= int(angle) <= 80:
            return int(angle)
        return default

    def _match_width_angle(self, width, angle):
        if width/angle > 20:
            return width, round(width/20)
        return width, angle

    def _get_thumb_heading(self, request, default):
        heading = request.query_params['heading']
        if heading.isdigit() and 0 <= int(heading) < 361:
            return int(heading)
        return default

    def _get_thumb_horizon(self, request, default):
        try:
            horizon = float(request.query_params['horizon'])
            if 0.0 <= horizon <= 1.0:
                return horizon
        except ValueError:
            return default

    def _get_thumb_aspect(self, request, default):
        try:
            aspect = float(request.query_params['aspect'])
            if aspect >= 1.0:
                return aspect
        except ValueError:
            return default

    def _get_heading(self, coords, geopoint):
        sql = "select 1 as id, degrees(st_azimuth(ST_GeogFromText('SRID=4326;POINT(%s %s)'), ST_GeogFromText('SRID=4326;POINT(%s %s)'))) AS heading "
        simpl = Panorama.objects.raw(sql, [geopoint[0], geopoint[1], coords[0], coords[1]])[0]
        return simpl.heading