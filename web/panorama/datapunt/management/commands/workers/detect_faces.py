import json
import time
from random import randrange

from datapunt.management.queue import Worker
from datasets.panoramas.regions import faces

DEFAULT_MIN_NEIGHBOURS = 6
NORMAL = 1
FLIPPED = -1

ZOOM_RANGE = [1, 1.08, 1.175, 1.29, 1.41]
SCALES = [1.15, 1.18, 1.22, 1.29]
SCALES1 = [1.067, 1.082, 1.099, 1.118]
SCALES2 = [1.016, 1.018, 1.021, 1.025]

CASCADE_SETS = [
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml",
     SCALES, DEFAULT_MIN_NEIGHBOURS, NORMAL, 'default'),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml",
     SCALES, DEFAULT_MIN_NEIGHBOURS-3, NORMAL, 'alt'),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml",
     SCALES, DEFAULT_MIN_NEIGHBOURS, NORMAL, 'alt2'),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml",
     SCALES1, DEFAULT_MIN_NEIGHBOURS, NORMAL, 'profile'),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_profileface.xml",
     SCALES1, DEFAULT_MIN_NEIGHBOURS, FLIPPED, 'profile_flip'),
    ("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml",
     SCALES2, 1, NORMAL, 'alt_tree')
]


class DetectFaces(Worker):
    _route = 'face_task'
    _route_out = 'face_done'

    def do_work_with_results(self, messagebody):
        message_dict = json.loads(messagebody.decode('utf-8'))

        rand_casc = randrange(0, len(CASCADE_SETS))
        if rand_casc + 1 is len(CASCADE_SETS):
            cascade = CASCADE_SETS[-1]
        else:
            rand_neighbour = randrange(2, 11)
            sel_cascade = CASCADE_SETS[rand_casc]
            cascade = (
                sel_cascade[0],
                sel_cascade[1],
                rand_neighbour,
                sel_cascade[3],
                sel_cascade[4],
            )

        rand_scale = randrange(0, len(cascade[1]))
        faces.CASCADE_SETS = [
            (
                cascade[0],
                cascade[1][rand_scale],
                cascade[2],
                cascade[3],
                cascade[4],
            )
        ]

        rand_zoom = randrange(0, len(ZOOM_RANGE))
        faces.ZOOM_RANGE = [ZOOM_RANGE[rand_zoom]]

        start_time = time.time()
        face_detector = faces.FaceDetector(message_dict['panorama_url'])

        regions = face_detector.get_face_regions()
        for region in regions:
            region[-1] += ', time={}ms'.format(int(round((time.time() - start_time) * 1000)))

        detected_by = "cascade={}, scaleFactor={}, zoom={}, time={}ms".format(
            cascade[4], cascade[1][rand_scale], faces.ZOOM_RANGE[0],
            int(round((time.time() - start_time) * 1000)))

        return [{'pano_id': message_dict['pano_id'],
                 'regions': regions,
                 'detected_by': detected_by}]
