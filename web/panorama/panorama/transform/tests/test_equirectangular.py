import os
import os.path
import logging

import numpy as np
from PIL import Image

from panorama.transform.equirectangular import rotate

log = logging.getLogger(__name__)

MAX_WIDTH = 2048
TILE_SIZE = 512
PREVIEW_WIDTH = 256


def test_rotate():
    here = os.path.dirname(__file__)
    datadir = here + "/../../../panoramas_test/2016/04/19/TMX7315120208-000033"
    filename = datadir + "/pano_0000_006658.jpg"
    # Resize image to make the test run faster.
    orig = Image.open(filename).resize((4000, 2000))

    im = orig
    im = rotate(im, 180, 50, 14, target_width=im.size[0])
    im = Image.fromarray(im.astype(np.uint8)).resize(orig.size)
    im = rotate(im, 180, -50, -14, target_width=im.size[0])
    im = Image.fromarray(im.astype(np.uint8)).resize(orig.size)

    # These two rotations should reproduce orig, but the resizing
    # can change some pixels so drastically that assert_allclose won't work.
    npixels = np.prod(orig.size)
    assert np.linalg.norm(np.asarray(im) - np.asarray(orig)) < 0.065 * npixels
