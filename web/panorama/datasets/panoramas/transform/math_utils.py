from numpy import array, sqrt, square, radians, float64, pi, arctan2, arccos, cos, sin, mod


def get_rotation_matrix(yaw, pitch, roll):
    r_pitch = radians(pitch)
    r_roll = radians(roll)
    r_yaw = radians(yaw)

    rx_roll = array(
        [
            [1, 0, 0],
            [0, cos(r_roll), -sin(r_roll)],
            [0, sin(r_roll), cos(r_roll)]
        ],
        dtype=float64
    )
    ry_pitch = array(
        [
            [cos(r_pitch), 0, sin(r_pitch)],
            [0, 1, 0],
            [-sin(r_pitch), 0, cos(r_pitch)]
        ],
        dtype=float64
    )
    rz_yaw = array(
        [
            [cos(r_yaw), -sin(r_yaw), 0],
            [sin(r_yaw), cos(r_yaw), 0],
            [0, 0, 1]
        ],
        dtype=float64
    )

    return rx_roll.dot(ry_pitch).dot(rz_yaw)


def cylindrical2cartesian(coordinates, source_width, source_height):
    middle = source_width / 2

    x = coordinates[0]
    y = coordinates[1]

    phi = (x - middle) * pi / middle
    theta = (y * pi) / source_height

    x1 = sin(theta)*cos(phi)
    y1 = sin(theta)*sin(phi)
    z1 = cos(theta)

    return x1, y1, z1


def rotate_cartesian_vectors(vector, matrix):
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

    r = 1 if r_is_1 else sqrt(square(x) + square(y) + square(z))
    theta = arccos(z/r)
    phi = arctan2(y, x)

    x1 = mod(middle + middle * phi / pi, source_width-1)
    y1 = source_height * theta / pi

    return x1, y1
