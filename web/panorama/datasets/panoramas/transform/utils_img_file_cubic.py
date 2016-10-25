from math import log

from PIL import Image

from datasets.panoramas.transform import utils_img_file as Img
from datasets.panoramas.transform import utils_math_cubic as Cube

TILE_SIZE=512
PREVIEW_WIDTH=256
MAX_WIDTH=2048


def save_as_file_set(cubic_dir, projections, max_width=MAX_WIDTH):
    previews = {}
    for side, img in projections.items():
        cube_face = Image.fromarray(img)
        preview = cube_face.resize((PREVIEW_WIDTH, PREVIEW_WIDTH), Image.ANTIALIAS)
        previews[side] = preview
        for zoomlevel in range(0, 1+int(log(max_width/TILE_SIZE, 2))):
            zoom_size = 2 ** zoomlevel * TILE_SIZE
            zoomed_img = cube_face.resize((zoom_size, zoom_size), Image.ANTIALIAS)
            for h_idx, h_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                for v_idx, v_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                    tile = zoomed_img.crop((h_start, v_start, h_start+TILE_SIZE, v_start+TILE_SIZE))
                    tile_path = "/{}/{}/{}".format(zoomlevel+1, side, v_idx)
                    Img.save_image(tile, "{}{}/{}.jpg".format(cubic_dir, tile_path, h_idx))

    preview_image = Image.new('RGB', (PREVIEW_WIDTH, 6 * PREVIEW_WIDTH))
    for idx, side in enumerate(Cube.CUBE_SIDES):
        preview_image.paste(previews[side], (0, PREVIEW_WIDTH*idx))
    Img.save_image(preview_image, cubic_dir+"/preview.jpg")

