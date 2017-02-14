import logging
from django.core.management import BaseCommand
from panorama.regions.batch import ImportRegions

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info('start importing regions')
        ImportRegions().process()

