import os
import logging
from unittest import mock, skipIf

import numpy as np
from PIL import Image

from panorama.transform.cubic import CubicTransformer
from . test_transformer import TestTransformer
from . test_img_file import mock_get_raw_pano

log = logging.getLogger(__name__)

MAX_WIDTH = 2048


@skipIf(not os.path.exists('/app/panoramas_test'),
        'Render test skipped: no mounted directory found, run in docker container')
class TestTransformImgCubic(TestTransformer):
    """
    This is more like an integration test than a unit test
    Because it expects a mounted /app/panoramas_test folder, run these in the Docker container

        docker exec -it panorama_web_1 ./manage.py test panorama.transform.tests.test_cubic

    look into the .gitignore-ed directory PROJECT/panoramas_test/output for a visual check on the transformations
    """
    @mock.patch('panorama.transform.utils_img_file.get_raw_panorama_as_rgb_array',
                side_effect=mock_get_raw_pano)
    def test_transform_cubic_runs_without_errors(self, _):
        for img in self.images:
            image_tranformer = CubicTransformer(img.path + img.filename, img.heading, img.pitch, img.roll)
            image_tranformer.project(target_width=MAX_WIDTH)


def test_cubic_random():
    r = np.random.randint(0, 256, (4000, 8000, 3), dtype=np.uint8)
    im = Image.fromarray(r, mode="RGB")
    t = CubicTransformer(pano_rgb=r)
    t.project()
