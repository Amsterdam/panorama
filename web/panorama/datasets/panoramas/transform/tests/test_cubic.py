# Python
import os, logging
from unittest import mock, skipIf
from math import log as logarithm
# Packages
from PIL import Image
from numpy import squeeze, dsplit
from scipy import misc
# Project
from datasets.panoramas.transform.cubic import CubicTransformer
from . test_transformer import TestTransformer

log = logging.getLogger(__name__)

MAX_WIDTH=2048
TILE_SIZE=512
PREVIEW_WIDTH=256


def set_pano(pano):
    global panorama
    panorama = pano


def mock_get_raw_pano(pano):
    path = '/app/panoramas_test/'+pano['container']+'/'+pano['name']
    panorama_image = misc.fromimage(Image.open(path))
    return squeeze(dsplit(panorama_image, 3))


@skipIf(not os.path.exists('/app/panoramas_test'),
        'Render test skipped: no mounted directory found, run in docker container')
class TestTransformImgCubic(TestTransformer):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.transform.tests.test_cubic

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """
    @mock.patch('datasets.panoramas.transform.img_file_utils.get_panorama_rgb_array',
                side_effect=mock_get_raw_pano)
    def test_transform_cubic_runs_without_errors(self, mock):

        for img in self.images:
            set_pano(img)
            image_tranformer = CubicTransformer(img.get_raw_image_objectstore_id(), img.heading, img.pitch, img.roll)
            output_path = "/app/test_output/"+img.filename[:-4]
            img_set = image_tranformer.get_projection(target_width=MAX_WIDTH)
            previews = {}
            for side, img in img_set.items():
                cube_face = Image.fromarray(img)
                preview = cube_face.resize((PREVIEW_WIDTH, PREVIEW_WIDTH), Image.ANTIALIAS)
                previews[side] = preview
                for zoomlevel in range(0, 1+int(logarithm(MAX_WIDTH/TILE_SIZE, 2))):
                    zoom_size = 2 ** zoomlevel * TILE_SIZE
                    zoomed_img = cube_face.resize((zoom_size, zoom_size), Image.ANTIALIAS)
                    for h_idx, h_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                        for v_idx, v_start in enumerate(range(0, zoom_size, TILE_SIZE)):
                            tile = zoomed_img.crop((h_start, v_start, h_start+TILE_SIZE, v_start+TILE_SIZE))
                            tile_path = "/{}/{}/{}".format(zoomlevel+1, side, v_idx)
                            os.makedirs(output_path+tile_path, exist_ok=True)
                            tile.save("{}{}/{}.jpg".format(output_path, tile_path, h_idx),  optimize=True, progressive=True)

            preview_image = Image.new('RGB', (PREVIEW_WIDTH, 6 * PREVIEW_WIDTH))
            for idx, side in enumerate(['b', 'd', 'f', 'l', 'r', 'u']):
                preview_image.paste(previews[side], (0,PREVIEW_WIDTH*idx))
            preview_image.save(output_path+"/preview.jpg", "JPEG", optimize=True, progressive=True)
