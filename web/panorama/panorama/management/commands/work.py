from threading import Thread

from django.core.management import BaseCommand

from panorama.tasks import workers


class Command(BaseCommand):
    def handle(self, *args, **options):
        for worker in workers.workers:
            Thread(target=worker().listen_for).start()
