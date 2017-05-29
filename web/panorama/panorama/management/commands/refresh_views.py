import logging

from django.core.management import BaseCommand
from django.db import connection
from django.conf import settings

log = logging.getLogger(__name__)


class Command(BaseCommand):
    views = ['panoramas_adjacencies', 'panoramas_recent_ids_all']
    for year in settings.PREPARED_YEARS:
        views.append(f"panoramas_recent_ids_{year}")

    def handle(self, *args, **options):
        self.refresh_views()

    def refresh_views(self, conn=None):
        if not conn:
            conn = connection

        for view in self.views:
            with conn.cursor() as cursor:
                self.stdout.write(f'refreshing materialized view {view}')
                cursor.execute(f"REFRESH MATERIALIZED VIEW public.{view}")

        self.stdout.write('refresh {} views'.format(len(self.views)))
