import logging

from datasets.panoramas.models import Panorama
from job import render
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class PanoRenderer(PanoProcessor):
    status_queryset = Panorama.to_be_rendered
    status_in_progress = Panorama.STATUS.rendering
    status_done = Panorama.STATUS.rendered

    def process_one(self, panorama: Panorama):
        render(panorama.path + panorama.filename, panorama.heading, panorama.pitch, panorama.roll)
