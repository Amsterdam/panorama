# Python
import logging

from django.db import transaction

from datasets.panoramas.models import Panorama
from datasets.shared.object_store import ObjectStore
from job import render

log = logging.getLogger(__name__)


class RenderPanorama:
    object_store = ObjectStore()

    def process(self):
        while True:
            pano_to_render = self._get_next_pano_to_render()
            if not pano_to_render:
                break

            log.info('RENDERING panorama: %s', str(pano_to_render))
            render(pano_to_render.path+pano_to_render.filename,
                   pano_to_render.heading,
                   pano_to_render.pitch,
                   pano_to_render.roll)

            self._set_renderstatus_to(pano_to_render, Panorama.STATUS.rendered)

    @transaction.atomic
    def _get_next_pano_to_render(self):
        try:
            pano_to_render = Panorama.to_be_rendered.select_for_update()[0]
            self._set_renderstatus_to(pano_to_render, Panorama.STATUS.rendering)
            return pano_to_render
        except IndexError:
            return None

    @transaction.atomic
    def _set_renderstatus_to(self, panorama, status):
        panorama.status = status
        panorama.save()
