# Python
import logging
# Packages
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
# Project
# from datasets.bag.models import Verblijfsobject
# from datasets.wkpb.models import Beperking


log = logging.getLogger(__name__)


def health(request):
    # check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except:
        log.exception("Database connectivity failed")
        return HttpResponse(
            "Database connectivity failed",
            content_type="text/plain", status=500)

    # check elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception("Elasticsearch connectivity failed")
        return HttpResponse(
            "Elasticsearch connectivity failed",
            content_type="text/plain", status=500)

    # check wkpd

    return HttpResponse(
        "Connectivity OK", content_type='text/plain', status=200)


def check_data(request):
    # check bag
    # try:
    #     assert Verblijfsobject.objects.count() > 10
    # except:
    #     log.exception("No BAG data found")
    #     return HttpResponse(
    #         "No BAG data found",
    #         content_type="text/plain", status=500)
    #
    # # check wkpb
    # try:
    #     assert Beperking.objects.count() > 10
    # except:
    #     log.exception("No WKPD data found")
    #     return HttpResponse(
    #         "No WKPD data found",
    #         content_type="text/plain", status=500)

    # check elastic
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert Search().using(client).index(
            settings.ELASTIC_INDICES['NUMMERAANDUIDING'],
            settings.ELASTIC_INDICES['BAG']).query("match_all", size=0)
    except:
        log.exception("Autocomplete failed")
        return HttpResponse(
            "Autocomplete failed", content_type="text/plain", status=500)

    return HttpResponse("Data OK", content_type='text/plain', status=200)
