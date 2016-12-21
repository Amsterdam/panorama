import json
import logging
import time

from datapunt.management.queue import Worker
from datasets.panoramas.regions import faces

log = logging.getLogger(__name__)


class DetectFaces(Worker):
    _route = 'face_task'
    _route_out = 'face_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        start_time = time.time()
        face_detector = faces.FaceDetector(message_dict['panorama_url'])

        regions = face_detector.get_opencv_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        return [{'pano_id': message_dict['pano_id'],
                 'regions': regions}]
