# Python
import logging
# Packages
from django.conf import settings
from django.db import connection
from django.http import HttpResponse

from datasets.panoramas.models import Panoramas

log = logging.getLogger(__name__)


def health(request):
    # check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert(cursor.fetchone())
    except:
        log.exception("Database connectivity failed")
        return HttpResponse(
            "Database connectivity failed",
            content_type="text/plain", status=500)

    # check debug
    if settings.DEBUG:
        log.exception("Debug mode not allowed in production")
        return HttpResponse(
            "Debug mode not allowed in production",
            content_type="text/plain", status=500)

    # if Panoramas.objects.all().count() < 500000:
    #     return HttpResponse(
    #         "Too few Panoramas in the database",
    #         content_type="text/plain", status=500)

    return HttpResponse(
        "Health OK", content_type='text/plain', status=200)
