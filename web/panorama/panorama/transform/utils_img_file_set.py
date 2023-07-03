from math import log
from typing import Iterator

from PIL import Image

from panorama.transform import cubic
from panorama.transform import utils_img_file as Img

TILE_SIZE = 512
PREVIEW_WIDTH = 256
MAX_WIDTH = 2048


def make_equirectangular(panorama_path, array_image) -> Iterator[tuple[str, Image.Image]]:
    """Make client images in equirectangular projection, at several resolutions.

    Generates (path, image) pairs.
    """

    base_panorama_dir = panorama_path[:-4]
    equirectangular_dir = base_panorama_dir + '/equirectangular/'

    image = Image.fromarray(array_image)
    yield equirectangular_dir + "panorama_8000.jpg", image
    medium_img = image.resize((4000, 2000), Image.ANTIALIAS)
    yield equirectangular_dir + "panorama_4000.jpg", medium_img
    small_img = image.resize((2000, 1000), Image.ANTIALIAS)
    yield equirectangular_dir + "panorama_2000.jpg", small_img


def make_cubic(panorama_path, array_image, max_width=MAX_WIDTH) -> Iterator[tuple[str, Image.Image]]:
    """
    Saves a set of cubic projections (the 6 sides of maximum resolution)
    as a Marzipano fileset

    :param max_width: the maximum cubesize
    """
    base_panorama_dir = panorama_path[:-4]
    cubic_dir = base_panorama_dir + '/cubic'
    rgb = Img.get_rgb_channels_from_array_image(array_image)
    projections = cubic.project(rgb, target_width=MAX_WIDTH)

    previews = {}
    for side, img_array in projections.items():
        cube_face = Image.fromarray(img_array)
        preview = cube_face.resize((PREVIEW_WIDTH, PREVIEW_WIDTH), Image.ANTIALIAS)
        previews[side] = preview
        for zoomlevel in range(0, 1+int(log(max_width/TILE_SIZE, 2))):
            zoom_size = 2 ** zoomlevel * TILE_SIZE
            zoomed_img = cube_face.resize((zoom_size, zoom_size), Image.ANTIALIAS)
            for h_idx, h_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                for v_idx, v_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                    tile = zoomed_img.crop((h_start, v_start, h_start+TILE_SIZE, v_start+TILE_SIZE))
                    tile_path = "/{}/{}/{}".format(zoomlevel+1, side, v_idx)
                    yield "{cubic_dir}{tile_path}/{h_idx}.jpg", tile

    preview_image = Image.new('RGB', (PREVIEW_WIDTH, 6 * PREVIEW_WIDTH))
    for idx, side in enumerate(cubic.SIDES):
        preview_image.paste(previews[side], (0, PREVIEW_WIDTH*idx))
    yield cubic_dir + "/preview.jpg", preview_image

