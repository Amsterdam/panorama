import numpy as np
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
    mid = len(x) / 2

    phi = (x - mid) * (np.pi / mid)
    theta = y * (np.pi / len(y))

    sin_theta = np.sin(theta).reshape(-1, 1)
    x1 = sin_theta * np.cos(phi).reshape(1, -1)
    y1 = sin_theta * np.sin(phi).reshape(1, -1)
    z1 = np.cos(theta).repeat(len(x)).reshape(len(y), len(x))

    return x1, y1, z1


def rotate_cartesian_vectors(vector, matrix):
    # TODO rewrite as numpy.dot.
    x = vector[0]
    y = vector[1]
    z = vector[2]

    m = matrix

    # perform matrix multiplication
    x1 = m[0][0] * x + m[0][1] * y + m[0][2] * z
    y1 = m[1][0] * x + m[1][1] * y + m[1][2] * z
    z1 = m[2][0] * x + m[2][1] * y + m[2][2] * z

    return x1, y1, z1


def cartesian2cylindrical(vector, source_width, source_height, r_is_1=True):
    middle = source_width / 2

    x = vector[0]
    y = vector[1]
    z = vector[2]

    if not r_is_1:
        r = np.linalg.norm([x, y, z])
        z = z / r
    theta = np.arccos(z)
    phi = np.arctan2(y, x)

    x1 = np.mod((middle / np.pi) * (phi + np.pi), source_width - 1)
    y1 = theta * (source_height / np.pi)

    return x1, y1
