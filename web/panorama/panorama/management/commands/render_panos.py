from django.core.management import BaseCommand

from panorama.tasks.render_task import RenderPanorama


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.render_panos()

    def render_panos(self):
        RenderPanorama().process()
