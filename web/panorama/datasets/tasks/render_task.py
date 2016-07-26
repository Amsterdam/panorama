# Python
import logging

from django.db import transaction
from scipy import misc

from datasets.panoramas.models import Panorama
from datasets.panoramas.transform.transformer import PanoramaTransformer
from datasets.tasks.models import RenderTask

log = logging.getLogger(__name__)


class RenderPanorama:
    def process(self):
        while True:
            pano_id = self._get_next_pano_id()
            if not pano_id:
                break

            log.info('RENDERING panorama: %s', pano_id)
            pano_to_render = Panorama.objects.filter(pano_id=pano_id)[0]
            pt = PanoramaTransformer(pano_to_render)
            rendered = pt.get_translated_image(target_width=8000)
            misc.imsave(pano_to_render.get_full_rendered_path(), rendered)

    @transaction.atomic
    def _get_next_pano_id(self):
        try:
            task = RenderTask.objects.all()[0]
            pano_id = task.pano_id
            task.delete()
            return pano_id
        except IndexError:
            return None
