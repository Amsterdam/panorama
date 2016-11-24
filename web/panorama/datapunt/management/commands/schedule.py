import logging
from threading import Thread

from django.core.management import BaseCommand

from . import listeners, schedulers

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for scheduler in schedulers.schedulers:
            Thread(target=scheduler().schedule).start()

        for listener in listeners.listeners:
            Thread(target=listener().listen_for).start()
