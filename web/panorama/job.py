import io
import sys
from math import log

from PIL import Image

from datasets.panoramas.transform.equirectangular import EquirectangularTransformer
from datasets.panoramas.transform.cubic import CubicTransformer
from datasets.shared import object_store

object_store = object_store.ObjectStore()

MAX_WIDTH=2048
TILE_SIZE=512
PREVIEW_WIDTH=256


def save_image(image, name):
    byte_array = io.BytesIO()
    image.save(byte_array, format='JPEG', optimize=True, progressive=True)
    object_store.put_into_datapunt_store(name, byte_array.getvalue(), 'image/jpeg')


def render(panorama_url, heading_in, pitch_in, roll_in):
    container = panorama_url.split('/')[0]
    name = panorama_url.replace(container+'/', '')
    objectstore_id = {'container':container, 'name':name}

    yaw = float(heading_in)
    pitch = float(pitch_in)
    roll = float(roll_in)

    print('START RENDERING panorama: {} in equirectangular projection.'.format(panorama_url))
    equirectangular_dir = panorama_url[:-4]+'/equirectangular/'

    equi_t = EquirectangularTransformer(objectstore_id, yaw, pitch, roll)

    projection = equi_t.get_projection(target_width=8000)
    save_image(Image.fromarray(projection), equirectangular_dir+"panorama_8000.jpg")

    projection = equi_t.get_projection(target_width=4000)
    save_image(Image.fromarray(projection), equirectangular_dir+"panorama_4000.jpg")

    projection = equi_t.get_projection(target_width=2000)
    save_image(Image.fromarray(projection), equirectangular_dir+"panorama_2000.jpg")

    print('START RENDERING panorama: {} in cubic projection.'.format(panorama_url))
    cubic_dir = panorama_url[:-4]+'/cubic'

    # for less overhead reuse rotation_matrix and pano_rgb
    cubic_t = CubicTransformer(None, rotation_matrix=equi_t.rotation_matrix, pano_rgb=equi_t.pano_rgb)

    projections = cubic_t.get_projection(target_width=MAX_WIDTH)
    previews = {}
    for side, img in projections.items():
        cube_face = Image.fromarray(img)
        preview = cube_face.resize((PREVIEW_WIDTH, PREVIEW_WIDTH), Image.ANTIALIAS)
        previews[side] = preview
        for zoomlevel in range(0, 1+int(log(MAX_WIDTH/TILE_SIZE, 2))):
            zoom_size = 2 ** zoomlevel * TILE_SIZE
            zoomed_img = cube_face.resize((zoom_size, zoom_size), Image.ANTIALIAS)
            for h_idx, h_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                for v_idx, v_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                    tile = zoomed_img.crop((h_start, v_start, h_start+TILE_SIZE, v_start+TILE_SIZE))
                    tile_path = "/{}/{}/{}".format(zoomlevel+1, side, v_idx)
                    save_image(tile, "{}{}/{}.jpg".format(cubic_dir, tile_path, h_idx))

    preview_image = Image.new('RGB', (PREVIEW_WIDTH, 6 * PREVIEW_WIDTH))
    for idx, side in enumerate(['b', 'd', 'f', 'l', 'r', 'u']):
        preview_image.paste(previews[side], (0,PREVIEW_WIDTH*idx))
    save_image(preview_image, cubic_dir+"/preview.jpg")

if __name__ == "__main__":
    if not len(sys.argv) == 5:
        print("""
4 arguments required, please provide the following of the source Panorama:
    - panorama_url in objectstore,
    - heading in degrees,
    - pitch in degrees,
    - roll in degrees

for instance:
    ./job.py 2016/03/17/TMX7315120208-000020/pano_0000_000000.jpg 359.75457352539 -0.467467454247501 -0.446629825528845
        """)
    else:
        render(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
