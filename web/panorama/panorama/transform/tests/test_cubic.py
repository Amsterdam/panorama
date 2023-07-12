import logging
import os
import os.path

import numpy as np
from PIL import Image

from panorama.transform import cubic
from . test_img_file import mock_get_raw_pano


def test_cubic_no_rotation():
    here = os.path.dirname(__file__)
    datadir = here + "/../../../panoramas_test/2016/04/19/TMX7315120208-000033"
    filename = datadir + "/pano_0000_006658.jpg"
    im = Image.open(filename)

    p = cubic.project(np.asarray(im).transpose([2, 0, 1]), target_width=1024)
    for side, im in p.items():
        assert im.shape == (1024, 1024, 3)
        assert im.dtype == np.uint8
        expect = np.asarray(Image.open(f"{os.path.splitext(filename)[0]}_{side}.jpg"))
        assert np.linalg.norm(im.ravel() - expect.ravel()) / im.size < .1
