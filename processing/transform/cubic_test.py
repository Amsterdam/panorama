import os
import os.path

import numpy as np
from PIL import Image
import torch

from . import cubic


def test_cubic():
    here = os.path.dirname(__file__)
    datadir = here + "/testdata/2016/04/19/TMX7315120208-000033"
    filename = datadir + "/pano_0000_006658.jpg"

    im = np.asarray(Image.open(filename)).transpose([2, 0, 1])
    im = torch.as_tensor(im.copy())

    p = cubic.project(im, target_width=1024)
    for side, im in p.items():
        assert im.shape == (3, 1024, 1024)
        assert im.dtype == torch.uint8
        expect = np.asarray(Image.open(f"{os.path.splitext(filename)[0]}_{side}.jpg"))
        im = im.numpy().transpose([1, 2, 0])
        assert np.linalg.norm(im.ravel() - expect.ravel()) / im.size < 0.1
        #Image.fromarray(expect).show()
        #Image.fromarray(im).show()
