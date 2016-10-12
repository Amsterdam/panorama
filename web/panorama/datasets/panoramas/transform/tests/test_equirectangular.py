# Python
import os, logging
from unittest import mock, skipIf
# Packages
from PIL import Image
from numpy import squeeze, dsplit
from scipy import misc
# Project
from datasets.panoramas.transform.equirectangular import EquirectangularTransformer
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
class TestTransformImgEquirectangular(TestTransformer):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test datasets.panoramas.transform.tests.test_image

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """
    @mock.patch('datasets.panoramas.transform.img_file_utils.get_panorama_rgb_array',
                side_effect=mock_get_raw_pano)
    def test_transform_runs_without_errors(self, mock):

        for img in self.images:
            set_pano(img)
            image_tranformer = EquirectangularTransformer(img.get_raw_image_objectstore_id(),
                                                          img.heading, img.pitch, img.roll)
            output_path = "/app/test_output/"+img.filename[:-4]
            for direction in [0, 90, 180, 270]:
                img1 = image_tranformer.get_projection(target_width=900,
                                                       target_fov=80,
                                                       target_horizon=0.3,
                                                       target_heading=direction,
                                                       target_aspect=4/3)
                misc.imsave(output_path+"_{}.jpg".format(direction), img1)
                img1 = image_tranformer.get_projection(target_width=450,
                                                       target_fov=80,
                                                       target_horizon=0.3,
                                                       target_heading=direction,
                                                       target_aspect=4/3)
                misc.imsave(output_path+"_small_{}.jpg".format(direction), img1)

            img1 = image_tranformer.get_projection(target_width=8000)
            transformed = Image.fromarray(img1)
            transformed.save(output_path+"_8000.jpg", optimize=True, progressive=True)
            half_size = transformed.resize((4000, 2000), Image.ANTIALIAS)
            half_size.save(output_path+"_4000.jpg", optimize=True, progressive=True)
            smallest = transformed.resize((2000, 1000), Image.ANTIALIAS)
            smallest.save(output_path+"_2000.jpg", optimize=True, progressive=True)
