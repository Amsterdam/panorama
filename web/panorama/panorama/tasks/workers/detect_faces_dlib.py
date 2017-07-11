import logging
import time

from datasets.panoramas.models import Panorama
from panorama.regions import faces
from panorama.tasks.detection import save_regions, region_writer
from .pano_processor import PanoProcessor

log = logging.getLogger(__name__)


class DlibFaceDetector(PanoProcessor):
    status_queryset = Panorama.detected_1
    status_in_progress = Panorama.STATUS.detecting2
    status_done = Panorama.STATUS.detected_2

    def process_one(self, panorama: Panorama):
        start_time = time.time()
        face_detector = faces.FaceDetector(panorama.get_intermediate_url())

        regions = face_detector.get_dlib_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        save_regions(regions, panorama)
        region_writer(panorama, dlib=True)
