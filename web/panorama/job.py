import sys

from datasets.panoramas.transform import utils_img_file as Img
from datasets.panoramas.transform import utils_img_file_cubic as CubeImg
from datasets.panoramas.transform.equirectangular import EquirectangularTransformer
from datasets.panoramas.transform.cubic import CubicTransformer


def render(panorama_path, heading_in, pitch_in, roll_in):
    yaw = float(heading_in)
    pitch = float(pitch_in)
    roll = float(roll_in)

    print('START RENDERING panorama: {} in equirectangular projection.'.format(panorama_path))
    equirectangular_dir = panorama_path[:-4] + '/equirectangular/'

    equi_t = EquirectangularTransformer(panorama_path, yaw, pitch, roll)

    projection = equi_t.get_projection(target_width=2000)
    Img.save_array_image(projection, equirectangular_dir+"panorama_2000.jpg")

    projection = equi_t.get_projection(target_width=4000)
    Img.save_array_image(projection, equirectangular_dir+"panorama_4000.jpg")

    projection = equi_t.get_projection(target_width=8000)
    Img.save_array_image(projection, equirectangular_dir+"panorama_8000.jpg")

    print('START RENDERING panorama: {} in cubic projection.'.format(panorama_path))
    cubic_dir = panorama_path[:-4] + '/cubic'

    # for less overhead base cubic projection on normalized equirectangular pano_rgb
    cubic_t = CubicTransformer(None, rotation_matrix=equi_t.rotation_matrix,
                               pano_rgb=Img.get_rgb_channels_from_array_image(projection))
    projections = cubic_t.get_normalized_projection(target_width=CubeImg.MAX_WIDTH)
    CubeImg.save_as_file_set(cubic_dir, projections)

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
