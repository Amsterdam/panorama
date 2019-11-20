# Python
import logging
# Packages
from django.conf import settings
from django.db import connection
from django.http import HttpResponse

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

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT datname FROM pg_database where pg_database.datname=%s", ('panorama',))
    except:
        log.exception("Database panorama is not present")
        return HttpResponse(
            "Database panorama is not present",
            content_type="text/plain", status=500)

    # check debug
    if settings.DEBUG:
        log.exception("Debug mode not allowed in production")
        return HttpResponse(
            "Debug mode not allowed in production",
            content_type="text/plain", status=500)

    return HttpResponse(
        "Health OK", content_type='text/plain', status=200)
