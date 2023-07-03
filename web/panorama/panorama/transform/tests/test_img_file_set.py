import os

import numpy as np
from PIL import Image
import pytest

import panorama.transform.utils_img_file_set as ImgSet


def test_make_equirectangular():
    here = os.path.dirname(__file__)
    datadir = here + "/../../../panoramas_test/"

    # The ImgSet functions want a path of this form.
    input_path = "2016/04/19/TMX7315120208-000033/pano_0000_006658.jpg"
    im = Image.open(datadir + input_path)

    result = ImgSet.make_equirectangular(input_path, np.asarray(im))

    d = f"{input_path[:-4]}/equirectangular"
    for resolution in [8000, 4000, 2000]:
        path, im = next(result)
        expect = f"{d}/panorama_{resolution}.jpg"
        assert path == expect

        assert isinstance(im, Image.Image)
        assert im.width == resolution
        assert im.height == resolution // 2

    with pytest.raises(StopIteration):
        next(result)
