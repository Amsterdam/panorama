import logging

from datasets.panoramas.v1.models import Panorama
from panorama.transform.equirectangular import EquirectangularTransformer
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class PanoRenderer(PanoProcessor):
    status_queryset = Panorama.to_be_rendered
    status_in_progress = Panorama.STATUS.rendering
    status_done = Panorama.STATUS.rendered

    def process_one(self, panorama: Panorama):
        panorama_path = panorama.path + panorama.filename
        log.info('START RENDERING panorama: {} in equirectangular projection.'.format(panorama_path))

        equi_t = EquirectangularTransformer(panorama_path, panorama.heading, panorama.pitch, panorama.roll)
        projection = equi_t.get_projection(target_width=8000)

        intermediate_path = 'intermediate/{}'.format(panorama_path)
        log.info("saving intermediate: {}".format(intermediate_path))

        Img.save_array_image(projection, intermediate_path, in_panorama_store=True)
