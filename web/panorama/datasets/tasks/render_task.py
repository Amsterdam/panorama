# Python
import logging

# Package
from django.db import transaction
from scipy import misc

# Project
from datasets.panoramas.models import Panorama
from datasets.panoramas.transform.transformer import PanoramaTransformer
from datasets.tasks.models import RenderTask

log = logging.getLogger(__name__)


class RenderPanorama:

    def process(self):
        try:
            while True:
                pano_to_render = Panorama.objects.filter(pano_id=self._get_pano_id())[0]
                log.info('RENDERING panorama: %s', pano_to_render.pano_id)
                pt = PanoramaTransformer(pano_to_render)
                rendered = pt.get_translated_image(target_width=8000)
                misc.imsave(pano_to_render.get_full_rendered_path(), rendered)
        except IndexError:
            return None

    @transaction.atomic
    def _get_pano_id(self):
        try:
            task = RenderTask.objects.all()[0]
            pano_id = task.pano_id
            task.delete()
            return pano_id
        except IndexError:
            return None