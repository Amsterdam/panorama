import io
import os.path

from PIL import Image
import torch

from . import _images


def test_jpeg_from_tensor():
    im = torch.rand(3, 400, 800)
    im = _images.jpeg_from_tensor(im, quality=50)
    im = Image.open(io.BytesIO(im))

    assert im.size == (800, 400)


def test_tensor_from_jpeg():
    here = os.path.dirname(__file__)
    datadir = here + "/testdata/2016/04/19/TMX7315120208-000033"
    filename = datadir + "/pano_0000_006658.jpg"

    with open(filename, "rb") as f:
        im = _images.tensor_from_jpeg(f.read())

    assert im.dtype == torch.uint8
    assert im.shape == (3, 4000, 8000)

    # Test conversion round trip.
    im = _images.jpeg_from_tensor(im)
    #Image.open(io.BytesIO(im)).show()
