import logging

from django.core.management import BaseCommand
from django.db import connection
from django.conf import settings

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.refresh_views()

    def refresh_views(self, conn=None):
        if not conn:
            conn = connection

        with conn.cursor() as cursor:
            self.stdout.write('refreshing materialized view panoramas_recent_all')
            cursor.execute("REFRESH MATERIALIZED VIEW public.panoramas_recent_all")
