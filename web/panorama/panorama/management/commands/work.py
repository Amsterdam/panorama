from django.core.management import BaseCommand
from panorama.tasks.workers.worker import Worker


class Command(BaseCommand):
    def handle(self, *args, **options):
        Worker().do_work()
        # for worker in workers.workers:
        #     Thread(target=worker().listen_for).start()
