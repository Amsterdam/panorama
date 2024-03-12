from typing import Union

from numpy.typing import ArrayLike
import torch

from . import _math


def rotate(
    im: Union[ArrayLike, torch.Tensor],
    heading: float,
    pitch: float,
    roll: float,
    target_width: int,
    device=None,
):
    im = torch.as_tensor(im, device=device)

    if im.shape[0] != 3:
        raise ValueError(f"expected RGB along dim 0, got shape {im.shape}")
    if im.shape[2] != 2 * im.shape[1]:
        raise ValueError(f"wrong shape {im.shape}")

    r = _math.rotation_matrix(heading, pitch, roll)
    x, y = _rotation_grid(r, im, target_width, device=device)

    return _math.sample(im, x, y).round_().to(torch.uint8)


def _rotation_grid(rot: torch.Tensor, im: torch.Tensor, target_width: int, device=None):
    """Transform a rotation matrix into a sample grid with the desired width."""
    assert rot.shape == (3, 3)

    # Create a sampling grid.
    height, width = im.shape[1:]
    steps = width / target_width
    x = torch.arange(0, width, steps, dtype=torch.float32, device=device)
    y = torch.arange(0, height, steps, dtype=torch.float32, device=device)

    # Transform image coordinates in equirectangular projection to cartesian
    # vectors with r=1.
    x, y, z = _math.cartesian_from_cylindrical(x, y)
    z = z.expand(x.shape)
    x, y, z = _math.rotate_cartesian_vectors(rot, x, y, z)

    # Transform cartesian vectors back to equirectangular image coordinates.
    x, y = _math.cylindrical_from_cartesian(
        x,
        y,
        z,
        source_width=width,
        source_height=height,
    )
    return x, y
