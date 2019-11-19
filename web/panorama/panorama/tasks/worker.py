# Python
import logging
import time

from panorama.tasks.mixins import PanoramaTableAware
from panorama.tasks.utilities import reset_abandoned_work, call_for_close
from panorama.tasks.workers.blur_regions import RegionBlurrer
from panorama.tasks.workers.detect_all import AllRegionDetector
from panorama.tasks.workers.render_pano import PanoRenderer

log = logging.getLogger(__name__)


class Worker(PanoramaTableAware):
    def do_work(self):
        self.take_available_work()

        # Give other nodes time to finish
        time.sleep(600)

        # When running in the 100.000 tasks some fail (we're a bit too marginal on memory), reset status
        # and retry doing work on them
        reset_abandoned_work()
        self.take_available_work()

        # Notify Jenkins that job is done
        call_for_close()

        # back off of swarm when done (if this time = 0, each node will
        #   restart continuously when work is done)
        time.sleep(600)

    def take_available_work(self):
        with self.panorama_table_present():
            while self._still_work_to_do():
                # work is done in _still_work_to_do
                pass

    def _still_work_to_do(self):
        """
            The meat of the work is done in the process() method of the workers.
            That method returns true if there was a panorama to process for that stage.
            States are processed right to left (blurrer first), for maximum throughput
        """
        still_working = \
            RegionBlurrer().process() is True \
            or AllRegionDetector().process() is True \
            or PanoRenderer().process() is True

        return still_working
