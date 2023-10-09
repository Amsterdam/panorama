import io
import os.path

import pytest
import torch
from PIL import Image

from . import _images


def test_jpeg_from_tensor():
    im = torch.rand(3, 400, 800)
    im = _images.jpeg_from_tensor(im, quality=50)
    im = Image.open(io.BytesIO(im))

    assert im.size == (800, 400)


@pytest.mark.parametrize(
    "filename",
    [
        "pano_0000_006658.jpg",
        "pano_0000_006658_d.jpg",
    ],
)
def test_optimize_jpeg(filename: str):
    here = os.path.dirname(__file__)
    datadir = os.path.join(here, "testdata/2016/04/19/TMX7315120208-000033")
    filename = os.path.join(datadir, filename)

    with open(filename, "rb") as f:
        b = f.read()

    size = len(b)
    im = Image.open(io.BytesIO(b))
    width, height = im.size
    t = _images._tensor_from_image(im)

    im = _images._optimize_jpeg(b)
    assert len(im) < size  # Our test images are unoptimized.

    equal = (_images.tensor_from_jpeg(b) == t).all()
    assert equal, f"optimizing changed the image {filename}"


def test_resize():
    im = torch.rand(3, 400, 800).to(torch.uint8)
    assert _images._image_from_tensor(_images.resize(im, 400)).size == (400, 200)
    assert _images._image_from_tensor(_images.resize(im, 200)).size == (200, 100)


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
    # Image.open(io.BytesIO(im)).show()
