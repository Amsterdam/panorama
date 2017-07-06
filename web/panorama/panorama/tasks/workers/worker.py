# Python
import logging
import time

from django.db import transaction

from datasets.panoramas.models import Panorama
from panorama.tasks.mixins import PanoramaTableAware

log = logging.getLogger(__name__)


class Worker(PanoramaTableAware):
    def do_work(self):
        with self.panorama_table_present():
            while True:
                rendered_pano = self._get_next_pano(Panorama.rendered, Panorama.STATUS.detecting_lp)
                if not rendered_pano:
                    break
                time.sleep(15)

    @transaction.atomic
    def _get_next_pano(self, status_queryset, next_status):
        try:
            next_pano = status_queryset.select_for_update()[0]
            self._set_renderstatus_to(next_pano, next_status)
            return next_pano
        except IndexError:
            return None

    @transaction.atomic
    def _set_renderstatus_to(self, panorama, status):
        panorama.status = status
        panorama.save()
