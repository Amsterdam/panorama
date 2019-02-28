from django.core.management import BaseCommand
from panorama.etl.db_actions import restore_all


class Command(BaseCommand):
    help = """Load data on swarm"""

    def handle(self, *args, **options):
        restore_all()
