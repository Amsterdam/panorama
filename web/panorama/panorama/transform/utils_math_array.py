import numexpr as ne
import numpy as np
from numpy.lib.stride_tricks import as_strided
from scipy.spatial.transform import Rotation


def rotation_matrix(yaw, pitch, roll):
    r = Rotation.from_euler("zyx", [-yaw, pitch, roll], degrees=True)
    return r.as_matrix()


def cylindrical2cartesian(coordinates, source_width, source_height):
    middle = source_width / 2

    x, y = coordinates

    phi = (x - middle) * np.pi / middle
    theta = (y * np.pi) / source_height

    sin_theta = np.sin(theta)
    x1 = sin_theta * np.cos(phi)
    y1 = sin_theta * np.sin(phi)
    z1 = np.cos(theta)

    return x1, y1, z1


def cartesian_from_cylindrical(x, y):
    """Convert cylindrical to cartesian coordinates.

    Arguments are two aranges of coordinates along the x and y axes.
    """
    mid = len(x) / 2

    phi = (x - mid) * (np.pi / mid)
    theta = y * (np.pi / len(y))

    phi, theta = phi.reshape(1, -1), theta.reshape(-1, 1)

    sin_theta = np.sin(theta)
    x1 = sin_theta * np.cos(phi)
    y1 = sin_theta * np.sin(phi)
    z1 = np.cos(theta)

    return x1, y1, z1


def rotate_cartesian_vectors(vectors, r):
    x, y, z = vectors

    # perform matrix multiplication
    r00, r01, r02 = r[0][0], r[0][1], r[0][2]
    r10, r11, r12 = r[1][0], r[1][1], r[1][2]
    r20, r21, r22 = r[2][0], r[2][1], r[2][2]
    xr = ne.evaluate("r00 * x + r01 * y + r02 * z")
    yr = ne.evaluate("r10 * x + r11 * y + r12 * z")
    zr = ne.evaluate("r20 * x + r21 * y + r22 * z")

    return xr, yr, zr


def cartesian2cylindrical(vector, source_width, source_height, r_is_1=True):
    middle = source_width / 2

    x = vector[0]
    y = vector[1]
    z = vector[2]

    if not r_is_1:
        z = ne.evaluate("z / sqrt(x ** 2 + y ** 2 + z ** 2)")

    pi = np.pi
    x1 = ne.evaluate("(middle / pi * (arctan2(y, x) + pi)) % (source_width - 1)")
    y1 = ne.evaluate("arccos(z) * (source_height / pi)")

    # Correct shapes so x1 and y1 are both square and of the same size.
    x1, y1 = np.atleast_2d(x1), np.atleast_2d(y1)
    if x1.size == 1:
        x1 = as_strided(x1, (y1.shape[1], y1.shape[1]), (0, 0))
    elif x1.shape[0] == 1:
        x1 = as_strided(x1, (x1.shape[1], x1.shape[1]), (0, x1.strides[1]))
    if y1.size == 1:
        y1 = as_strided(y1, (x1.shape[0], x1.shape[0]), (0, 0))
    elif y1.shape[1] == 1:
        y1 = as_strided(y1, (y1.shape[0], y1.shape[0]), (y1.strides[0], 0))

    return x1, y1
