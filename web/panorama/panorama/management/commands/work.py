from django.core.management import BaseCommand

from panorama.tasks import worker


class Command(BaseCommand):
    def handle(self, *args, **options):
        worker.run()
