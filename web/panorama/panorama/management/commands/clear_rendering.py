from django.core.management import BaseCommand

from panorama.tasks.render_batch import RenderBatch


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.clear_rendering()

    def clear_rendering(self):
        RenderBatch().clear_rendering()
