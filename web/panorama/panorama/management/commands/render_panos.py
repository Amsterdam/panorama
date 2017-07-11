from django.core.management import BaseCommand

from panorama.tasks.workers.render_pano import PanoRenderer


class Command(BaseCommand):
    def handle(self, *args, **options):
        PanoRenderer().process_all()
