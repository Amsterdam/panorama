import os
import os.path
import logging

import numpy as np
from PIL import Image, ImageChops
import torch

from .equirectangular import rotate

log = logging.getLogger(__name__)

MAX_WIDTH = 2048
TILE_SIZE = 512
PREVIEW_WIDTH = 256


def test_rotate():
    here = os.path.dirname(__file__)
    datadir = here + "/testdata/2016/04/19/TMX7315120208-000033"
    filename = datadir + "/pano_0000_006658.jpg"

    # Resize image to make the test run faster.
    orig = Image.open(filename).resize((1000, 500))
    #orig.show()

    im = torch.tensor(np.asarray(orig).transpose([2, 0, 1]))

    # Rotate by 180 degrees twice.
    im = rotate(im, 180, 0, 0, target_width=orig.size[0])
    #Image.fromarray(im.numpy().transpose([1, 2, 0]), mode="RGB").show()

    im = rotate(im, 180, 0, 0, target_width=orig.size[0])
    #im = Image.fromarray(im.astype(np.uint8)).resize(orig.size)
    im = Image.fromarray(im.numpy().transpose([1, 2, 0]), mode="RGB")

    assert im.size == orig.size
    #im.show()

    # These two rotations should reproduce orig, at least approximately.
    # XXX We effectively test the average pixel value, which only catches some
    # errors. What is a good distance metric here?
    a, b = np.asarray(orig), np.asarray(im)
    assert np.linalg.norm(a - b) / np.prod(a.shape) < .1
