# Python
import io
import logging

from django.db import transaction
from scipy import misc

from datasets.panoramas.models import Panorama
from datasets.panoramas.transform.equirectangular import EquirectangularTransformer
from datasets.shared.object_store import ObjectStore

log = logging.getLogger(__name__)


class RenderPanorama:
    object_store = ObjectStore()

    def process(self):
        while True:
            pano_to_render = self._get_next_pano_to_render()
            if not pano_to_render:
                break

            log.info('RENDERING panorama: %s', str(pano_to_render))
            rendered_name = pano_to_render.path+pano_to_render.filename[:-4]+'_normalized.jpg'
            rendered_num_array = EquirectangularTransformer(pano_to_render.path+pano_to_render.filename,
                                                            pano_to_render.heading,
                                                            pano_to_render.pitch,
                                                            pano_to_render.roll
                                                           ).get_projection(target_width=8000)
            to_bytes = io.BytesIO()
            misc.toimage(rendered_num_array).save(to_bytes, format='jpeg')
            self.object_store.put_into_datapunt_store(rendered_name, to_bytes.getvalue(), 'image/jpeg')
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
