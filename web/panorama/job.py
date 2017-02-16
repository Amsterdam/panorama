import sys
import logging

from panorama.transform import utils_img_file as Img
from panorama.transform.equirectangular import EquirectangularTransformer

log = logging.getLogger(__name__)


def render(panorama_path, heading_in, pitch_in, roll_in):
    yaw = float(heading_in)
    pitch = float(pitch_in)
    roll = float(roll_in)

    log.info('START RENDERING panorama: {} in equirectangular projection.'.format(panorama_path))
    equi_t = EquirectangularTransformer(panorama_path, yaw, pitch, roll)
    projection = equi_t.get_projection(target_width=8000)

    intermediate_path = 'intermediate/{}'.format(panorama_path)
    log.info("saving intermediate: {}".format(intermediate_path))
    Img.save_array_image(projection, intermediate_path, in_panorama_store=True)

if __name__ == "__main__":
    if not len(sys.argv) == 5:
        print("""
4 arguments required, please provide the following of the source Panorama:
    - panorama_path in objectstore,
    - heading in degrees,
    - pitch in degrees,
    - roll in degrees

for instance:
    ./job.py 2016/03/17/TMX7315120208-000020/pano_0000_000000.jpg 359.75457352539 -0.467467454247501 -0.446629825528845
        """)
    else:
        render(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
