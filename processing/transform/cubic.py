import torch

from . import _math


CUBE_FRONT, CUBE_BACK, CUBE_LEFT, CUBE_RIGHT, CUBE_UP, CUBE_DOWN = (
    "f",
    "b",
    "l",
    "r",
    "u",
    "d",
)
#   preserve order - the preview.jpg in utils_img_file_set depends on it:
SIDES = [CUBE_BACK, CUBE_DOWN, CUBE_FRONT, CUBE_LEFT, CUBE_RIGHT, CUBE_UP]

MAX_CUBIC_WIDTH = 2048  # width of cubic edges


def project(im: torch.Tensor, target_width=MAX_CUBIC_WIDTH):
    """Returns cubic projections of an image.

    The image im must be of shape 3×H×W.

    :return: dictionary mapping SIDES to tensors.
    """
    assert len(im.shape) == 3
    assert im.shape[0] == 3
    return {side: _project_side(side, im, target_width) for side in SIDES}


def _project_side(side, im: torch.Tensor, width) -> torch.Tensor:
    x, y, z = _make_cube_side(side, width, im.device)

    x, y = _math.cylindrical_from_cartesian(
        x, y, z, source_width=im.shape[2], source_height=im.shape[1], r_is_1=False
    )

    return _math.sample(im, x, y)


def _make_cube_side(side, width, device):
    """Returns the cartesian coordinates of one side of a cube."""
    # u, d, f, b, l, r = up, down, front, back, left, right

    half_width = width / 2

    def arange(i, j, step):
        return torch.arange(i, j, step, device=device, dtype=torch.float32)

    if side == CUBE_FRONT:
        x = half_width
        y = arange(-half_width, half_width, 1).reshape(1, -1)
        z = arange(half_width, -half_width, -1).reshape(-1, 1)
    elif side == CUBE_BACK:
        x = -half_width
        y = arange(half_width, -half_width, -1).reshape(1, -1)
        z = arange(half_width, -half_width, -1).reshape(-1, 1)
    elif side == CUBE_LEFT:
        y = -half_width
        x = arange(-half_width, half_width, 1).reshape(1, -1)
        z = arange(half_width, -half_width, -1).reshape(-1, 1)
    elif side == CUBE_RIGHT:
        y = half_width
        x = arange(half_width, -half_width, -1).reshape(1, -1)
        z = arange(half_width, -half_width, -1).reshape(-1, 1)
    elif side == CUBE_UP:
        z = half_width
        y = arange(-half_width, half_width, 1).reshape(1, -1)
        x = arange(-half_width, half_width, 1).reshape(-1, 1)
    elif side == CUBE_DOWN:
        z = -half_width
        y = arange(-half_width, half_width, 1).reshape(1, -1)
        x = arange(half_width, -half_width, -1).reshape(-1, 1)
    else:
        raise ValueError("invalid side")

    x = torch.as_tensor(x, device=device)
    y = torch.as_tensor(y, device=device)
    z = torch.as_tensor(z, device=device)

    return x, y, z
