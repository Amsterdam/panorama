import logging

from datasets.panoramas.models import Panoramas
from panorama.transform.equirectangular import EquirectangularTransformer
from panorama.transform.utils_img_file import save_array_image
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class PanoRenderer(PanoProcessor):
    status_queryset = Panoramas.to_be_rendered
    status_in_progress = Panoramas.STATUS.rendering
    status_done = Panoramas.STATUS.rendered

    def process_one(self, panorama: Panoramas):
        panorama_path = panorama.path + panorama.filename
        log.info('START RENDERING panorama: {} in equirectangular projection.'.format(panorama_path))

        equi_t = EquirectangularTransformer(panorama_path, panorama.heading, panorama.pitch, panorama.roll)
        projection = equi_t.get_projection(target_width=8000)

        intermediate_path = 'intermediate/{}'.format(panorama_path)
        log.info("saving intermediate: {}".format(intermediate_path))

        save_array_image(projection, intermediate_path, in_panorama_store=True)
