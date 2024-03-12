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
    assert p.keys() == set(cubic.SIDES)
    for side, im in p.items():
        assert im.shape == (3, 1024, 1024)
        expect = np.asarray(Image.open(f"{os.path.splitext(filename)[0]}_{side}.jpg"))
        im = im.round().to(torch.uint8).numpy().transpose([1, 2, 0])
        assert np.linalg.norm(im.ravel() - expect.ravel()) / im.size < 0.1
        # Image.fromarray(expect).show()
        # Image.fromarray(im).show()


def test_fileset():
    here = os.path.dirname(__file__)
    datadir = here + "/testdata/2016/04/19/TMX7315120208-000033"
    filename = datadir + "/pano_0000_006658.jpg"

    im = np.asarray(Image.open(filename)).transpose([2, 0, 1])
    im = torch.as_tensor(im.copy())

    p = cubic.project(im, target_width=1024)

    fileset = dict(cubic.make_fileset(p))

    assert fileset.keys() == {
        template.format(side)
        for side in cubic.SIDES
        for template in (
            "1/{}/0/0.jpg",
            "2/{}/0/0.jpg",
            "2/{}/1/0.jpg",
            "2/{}/0/1.jpg",
            "2/{}/1/1.jpg",
            "3/{}/0/0.jpg",
            "3/{}/1/0.jpg",
            "3/{}/2/0.jpg",
            "3/{}/3/0.jpg",
            "3/{}/0/1.jpg",
            "3/{}/1/1.jpg",
            "3/{}/2/1.jpg",
            "3/{}/3/1.jpg",
            "3/{}/0/2.jpg",
            "3/{}/1/2.jpg",
            "3/{}/2/2.jpg",
            "3/{}/3/2.jpg",
            "3/{}/0/3.jpg",
            "3/{}/1/3.jpg",
            "3/{}/2/3.jpg",
            "3/{}/3/3.jpg",
            "preview.jpg",
        )
    }

    for key, im in fileset.items():
        assert im.dtype == torch.uint8
        if key == "preview.jpg":
            height = (
                6 * cubic._PREVIEW_WIDTH
                if key == "preview.jpg"
                else cubic._PREVIEW_WIDTH
            )
            assert im.shape == (3, height, cubic._PREVIEW_WIDTH)
