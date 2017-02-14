import json
import logging
import time

from panorama.tasks.queue import Worker
from panorama.regions import faces

log = logging.getLogger(__name__)


class DetectProfiles(Worker):
    _route = 'detect_profile_task'
    _route_out = 'profile_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        start_time = time.time()
        face_detector = faces.FaceDetector(message_dict['panorama_url'])
        faces.CASCADE_SETS = [
            ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml",
             1.11, 5, faces.FLIPPED, 'profile_flip_correct'),
        ]

        regions = face_detector.get_opencv_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        return [{'pano_id': message_dict['pano_id'],
                 'regions': regions}]
