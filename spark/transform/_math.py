# Common math utilities.

from kornia.geometry.transform import remap
from scipy.spatial.transform import Rotation
import torch
from torch import pi


def rotation_matrix(yaw: float, pitch: float, roll: float) -> torch.Tensor:
    """Returns a 3×3 rotation matrix of -yaw, pitch and roll."""
    r = Rotation.from_euler("zyx", [-yaw, pitch, roll], degrees=True)
    r = r.as_matrix()
    return torch.as_tensor(r, dtype=torch.float32)


def cartesian_from_cylindrical(x: torch.Tensor, y: torch.Tensor):
    """Convert cylindrical pixel coordinates to cartesian coordinates
    of points on the unit sphere.

    Arguments are two aranges of coordinates along the x and y axes.
    """
    if not x.dtype.is_floating_point:
        x = x.to(torch.float32)
    if not y.dtype.is_floating_point:
        y = y.to(torch.float32)

    mid = x.shape[0] / 2

    phi = (x - mid).mul_(pi / mid)
    theta = y * (pi / len(y))

    phi, theta = phi.reshape(1, -1), theta.reshape(-1, 1)

    sin_theta = theta.sin()
    x = sin_theta * phi.cos()
    y = sin_theta * phi.sin_()
    z = theta.cos_()

    return x, y, z.expand(x.shape)


def rotate_cartesian_vectors(r, x, y, z):
    """Rotates vectors with the given x, y and z coordinates
    according to the 3×3 matrix r.
    """
    if x.device != y.device or y.device != z.device:
        msg = f"want x,y,z on the same device, got {x.device},{y.device},{z.device}"
        raise ValueError(msg)

    r = torch.as_tensor(r, dtype=x.dtype, device=x.device)
    shape = x.shape
    x, y, z = x.reshape(-1, 1), y.reshape(-1, 1), z.reshape(-1, 1)

    # Shorter, but slower on CPU:
    # xyz = torch.hstack([x, y, z])
    # x, y, z = torch.mm(r, xyz.T, out=xyz.T)

    xyz = r[:, 0] * x
    xyz = xyz.addcmul_(r[:, 1], y)
    xyz = xyz.addcmul_(r[:, 2], z)
    xyz = xyz.T.reshape(3, *shape)
    x, y, z = xyz

    return x, y, z


def cylindrical_from_cartesian(
    x: torch.Tensor,
    y: torch.Tensor,
    z: torch.Tensor,
    source_width: int,
    source_height: int,
    r_is_1=True,
) -> torch.Tensor:
    """Convert cartesian coordinates to cylindrical pixel coordinates."""
    if r_is_1:
        z = z.clone()  # Allow us to overwrite z with acos_.
    else:
        # z = z / sqrt(x**2 + y**2 + z**2)
        X, Y, Z = sorted([x, y, z], key=torch.numel)
        shape = max(Y.shape), max(Z.shape)
        z = z / X.square().repeat(shape).addcmul_(Y, Y).addcmul_(Z, Z).sqrt_()

    middle = source_width / 2
    x = y.atan2(x).add_(pi).mul_(middle / pi).remainder_(source_width)
    y = z.acos_().mul_(source_height / pi)

    if x.numel() < y.numel():
        x = x.expand_as(y)
    else:
        y = y.expand_as(x)

    return x, y


def sample(im: torch.Tensor, x: torch.Tensor, y: torch.Tensor):
    """Sample image at the grid positions x, y.

    Returns a tensor of shape 3×H×W.
    """
    # Kornia (actually torch.nn.functional.grid_sample) wants a batch of images,
    # B×C×H×W. Since our rotation matrix is different for each image, we process
    # batches of one.
    im = im.reshape(1, *im.shape)
    x = x.reshape(1, *x.shape)
    y = y.reshape(1, *y.shape)

    # Prevent "RuntimeError: grid_sampler_2d_cpu not implemented for Byte".
    # XXX Is torch.uint8 supported on CUDA?
    im = im.to(torch.float32)
    # These should be float32, but convert just in case.
    x = x.to(torch.float32)
    y = y.to(torch.float32)

    im = remap(im, x, y, padding_mode="reflection")[0]
    im = im.round_().to(torch.uint8)
    return im
