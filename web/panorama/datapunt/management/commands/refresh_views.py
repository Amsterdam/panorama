from django.core.management import BaseCommand
from django.db import connection

GEO_VIEW_PREFIX = 'geo_'


class Command(BaseCommand):
    views = ['panoramas_adjacencies']

    def handle(self, *args, **options):
        self.refresh_views()

    def refresh_views(self):
        cursor = connection.cursor()

        for view in self.views:
            self.stdout.write('refreshing materialized view {}'.format(view))
            cursor.execute("REFRESH MATERIALIZED VIEW {}".format(view))

        self.stdout.write('refresh {} views'.format(len(self.views)))
