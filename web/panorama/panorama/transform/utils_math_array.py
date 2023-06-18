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
    xr = r[0][0] * x + r[0][1] * y + r[0][2] * z
    yr = r[1][0] * x + r[1][1] * y + r[1][2] * z
    zr = r[2][0] * x + r[2][1] * y + r[2][2] * z

    return xr, yr, zr


def cartesian2cylindrical(vector, source_width, source_height, r_is_1=True):
    middle = source_width / 2

    x = vector[0]
    y = vector[1]
    z = vector[2]

    if not r_is_1:
        r = np.sqrt(np.square(x) + np.square(y) + np.square(z))
        z = z / r
    theta = np.arccos(z)
    phi = np.arctan2(y, x)

    x1 = np.mod((middle / np.pi) * (phi + np.pi), source_width - 1)
    y1 = theta * (source_height / np.pi)

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
