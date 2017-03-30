import json
import logging
import time

from panorama.tasks.queue import BaseWorker
from panorama.regions import faces

log = logging.getLogger(__name__)


class DetectFacesGoogle(BaseWorker):
    _route = 'detect_face3_task'
    _route_out = 'face3_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        start_time = time.time()
        face_detector = faces.FaceDetector(message_dict['panorama_path'])

        regions = face_detector.get_vision_api_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        return [{'pano_id': message_dict['pano_id'],
                 'regions': regions}]
