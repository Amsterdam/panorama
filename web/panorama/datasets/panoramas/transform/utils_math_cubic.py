from math import pi, tan, sqrt, cos, sin

CUBE_FRONT, CUBE_BACK, CUBE_LEFT, CUBE_RIGHT, CUBE_UP, CUBE_DOWN = 'f', 'b', 'l', 'r', 'u', 'd'
#   preserve order - the preview.jpg in utils_img_file_cubic depends on it.
CUBE_SIDES = [CUBE_BACK, CUBE_DOWN, CUBE_FRONT, CUBE_LEFT, CUBE_RIGHT, CUBE_UP]

MAX_CUBIC_WIDTH = 2048  # width of cubic edges

HORIZON_START_ANGLES = [
    (CUBE_FRONT, -0.25*pi),
    (CUBE_LEFT, 0.25*pi),
    (CUBE_BACK, 0.75*pi),
    (CUBE_RIGHT, 1.25*pi),
    (CUBE_FRONT, 1.75*pi)
]


def _get_side_per_angle(phi):
    return [side for (side, angle) in HORIZON_START_ANGLES if angle < phi][-1]


def _get_start_angle_per_side(on_side):
    return [angle for (side, angle) in HORIZON_START_ANGLES if side is on_side][0]


def _get_coordinate_on_cube_side(phi, theta):
    on_side = _get_side_per_angle(phi)
    rotation_for_side = _get_start_angle_per_side(on_side) + 0.25 * pi

    half_width = MAX_CUBIC_WIDTH / 2
    x = half_width * tan(phi-rotation_for_side)

    r_on_horizon = sqrt((x - half_width)**2 + half_width**2)
    angle_from_horizon = 0.5*pi - theta
    if abs(angle_from_horizon) > 1:
        # make sure y is outside image, on the correct plane
        y = (1 - 1.1 * angle_from_horizon) * half_width
    else:
        y = half_width - r_on_horizon * tan(angle_from_horizon)

    if y < 0 or y > MAX_CUBIC_WIDTH:
        on_side, direction = (CUBE_UP, 1) if y < 0 else (CUBE_DOWN, -1)
        r_in_plane = half_width * tan(phi)
        x = half_width - r_in_plane * sin(phi)
        y = half_width - direction * r_in_plane * cos(phi)

    return on_side, (int(x), int(y))


def equirectangular2cubic_coordinates(coordinates, source_width, source_height):
    middle = source_width / 2

    x = coordinates[0]
    y = coordinates[1]

    phi = (x - middle) * pi / middle
    theta = (y * pi) / source_height

    return _get_coordinate_on_cube_side(phi, theta)

