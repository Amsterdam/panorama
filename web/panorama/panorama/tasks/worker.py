# Python
import logging
import time

from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.workers.blur_regions import RegionBlurrer
from panorama.tasks.workers.detect_faces import OpenCVFaceDetector
from panorama.tasks.workers.detect_faces_dlib import DlibFaceDetector
from panorama.tasks.workers.detect_faces_google import GoogleFaceDetector
from panorama.tasks.workers.detect_lps import LicensePlateDetector
from panorama.tasks.workers.render_pano import PanoRenderer

log = logging.getLogger(__name__)


class Worker(PanoramaTableAware):
    def do_work(self):
        with self.panorama_table_present():
            while self._still_work_to_do():
                pass

        # back off of swarm when done (if this time = 0, each node will
        #   restart continuously when work is done)
        time.sleep(1200)

    def _still_work_to_do(self):
        """
            The meat of the work is done in the process() method of the workers.
            That method returns true if there was a panorama to process for that stage.
            States are processed right to left (blurrer first), for maximum throughput
        """
        still_working = \
            RegionBlurrer().process() == True \
            or GoogleFaceDetector().process() == True \
            or DlibFaceDetector().process() == True \
            or OpenCVFaceDetector().process() == True \
            or LicensePlateDetector().process() == True \
            or PanoRenderer().process() == True

        return still_working
