from django.core.management import BaseCommand

from datasets.tasks.render_batch import CreateRenderBatch


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.create_renderbatch()

    def create_renderbatch(self):
        CreateRenderBatch().process()