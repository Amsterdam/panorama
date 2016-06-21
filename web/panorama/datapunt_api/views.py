# Packages
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
# Project
from datasets.panoramas.mixins import ViewLocationMixin, DateConversionMixin
from datasets.panoramas.models import Panorama
from datasets.panoramas.serializers import PanoSerializer


class PanoViewSet(ViewLocationMixin, DateConversionMixin, viewsets.ModelViewSet):
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

        Required Parameters:
        lat/lon for wgs84 coords or x/y for RD coords, float or int values

        Optional Parameters:
        radius: (int) denoting search radius in meters
        vanaf and/or tot: Several valued are allowed:
            - (int) timestamp
            - (int) year
            - (string) ISO date format yyyy-mm-dd.
            - (string) Eu date formate dd-mm-yyyy.
            if vanaf and tot are given, tot must be bigger then vanaf
        """
        pano = []
        # Make sure a position is given, otherwise there is
        # nothing to work with
        coords = self._get_request_coord(request.query_params)
        if coords:
            sql_where = []
            sql_params = []
            sql_get_pano = " SELECT * FROM panoramas_panorama "
            if  'radius' in request.query_params:
                max_range = request.query_params['radius']
                # Making sure radius is a positive int
                if max_range.isdigit():
                    max_range = int(max_range)
                    sql_where.append(" ST_DWithin(ST_GeogFromText('SRID=4326;POINT(%s %s)'), geography(geolocation), %s) ")
                    sql_params.extend([coords[0], coords[1], max_range])
            if 'vanaf' in request.query_params:
                start_date = self._convert_to_date(request.query_params['vanaf'])
                if start_date:
                    sql_where.append(" timestamp > %s ")
                    sql_params.append(start_date)
            if 'tot' in request.query_params:
                end_date = self._convert_to_date(request.query_params['tot'])
                if end_date:
                    sql_where.append(" timestamp <= %s ")
                    sql_params.append(end_date)
            sql_nearest = " ORDER BY geolocation <-> 'SRID=4326;POINT(%s %s)' limit 1 "
            sql_params.extend([coords[0], coords[1]])
            if len(sql_where) > 0:
                sql = sql_get_pano + " WHERE " + " AND ".join(sql_where) + sql_nearest
            else:
                sql = sql_get_pano + sql_nearest
            try:
                pano = Panorama.objects.raw(sql, sql_params)[0]
                pano = PanoSerializer(pano, context={'request': request}).data
            except IndexError:
                # No results were found
                pano = []
        else:
            pano = {'error': 'Geen coordinaten gevonden'}
        return Response(pano)

    def retrieve(self, request, pk=None):
        pano = get_object_or_404(Panorama, pano_id=pk)
        resp = PanoSerializer(pano, context={'request': request})
        return Response(resp.data)


