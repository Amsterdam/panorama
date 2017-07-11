from django.core.management import BaseCommand

from panorama.tasks.worker import Worker


class Command(BaseCommand):
    def handle(self, *args, **options):
        Worker().do_work()
