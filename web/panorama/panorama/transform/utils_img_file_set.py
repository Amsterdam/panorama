from math import log

from PIL import Image

from panorama.transform import cubic
from panorama.transform import utils_img_file as Img

TILE_SIZE = 512
PREVIEW_WIDTH = 256
MAX_WIDTH = 2048


def save_image_set(panorama_path, array_image):
    """
    Saves as a complete set of client images (equirectangular an cubic, in several resolutions)

    :param panorama_path: path of the panorama
    :param array_image: source of the image as a numpy array
    :return:
    """

    base_panorama_dir = panorama_path[:-4]
    equirectangular_dir = base_panorama_dir + '/equirectangular/'

    image = Image.fromarray(array_image)
    Img.save_image(image, equirectangular_dir+"panorama_8000.jpg")
    medium_img = image.resize((4000, 2000), Image.ANTIALIAS)
    Img.save_image(medium_img, equirectangular_dir+"panorama_4000.jpg")
    small_img = image.resize((2000, 1000), Image.ANTIALIAS)
    Img.save_image(small_img, equirectangular_dir+"panorama_2000.jpg")

    # save cubic set
    cubic_dir = base_panorama_dir + '/cubic'
    im = Img.get_rgb_channels_from_array_image(array_image)
    projections = cubic.project(im, target_width=MAX_WIDTH)
    save_as_cubic_file_set(cubic_dir, projections)


def save_as_cubic_file_set(cubic_dir, projections, max_width=MAX_WIDTH):
    """
    Saves a set of cubic projections (the 6 sides of maximum resolution)
    as a Marzipano fileset

    :param cubic_dir: target directory for the fileset
    :param projections: dict of 6 projections, keys are the faces of the cube
    :param max_width: the maximum cubesize
    :return:
    """
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
                    Img.save_image(tile, "{}{}/{}.jpg".format(cubic_dir, tile_path, h_idx))

    preview_image = Image.new('RGB', (PREVIEW_WIDTH, 6 * PREVIEW_WIDTH))
    for idx, side in enumerate(cubic.SIDES):
        preview_image.paste(previews[side], (0, PREVIEW_WIDTH*idx))
    Img.save_image(preview_image, cubic_dir+"/preview.jpg")

