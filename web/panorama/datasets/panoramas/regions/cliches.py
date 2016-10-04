from numpy import arange, meshgrid, mod

PANORAMA_WIDTH = 8000
PANORAMA_ANGLE = 360
HORIZON_X = 2000

# These settings are arbitrary, they seem to work
SAMPLE_BELOW_H = 100
SAMPLE_X = HORIZON_X + SAMPLE_BELOW_H
SAMPLE_WIDTH = 750
SAMPLE_HEIGHT = 500
SAMPLE_MAGNIFICATION = 1.25
SAMPLE_ANGLE = 22.5

SAMPLE_SHIFTS = [0.075, 0.175, 0.300, 0.450, 0.625]

HALF_WIDTH = SAMPLE_WIDTH / 2


class Cliche:
    """
    Represents a set of coordinates to be sampled out of a panorama, with a (simplified) shift in falling lines
    and offering the possibility to recalculate original x, y in panorama from the x, y in sample-set.
    """
    def __init__(self, x, y, base_shift, shift_direction):
        self.base_shift = base_shift
        self.shift_direction = shift_direction

        self.y_mid = HALF_WIDTH + y[0][0]
        self.shift_factor = self.shift_direction * self.base_shift / HALF_WIDTH

        self.x = self.shift_x(x, y)
        self.y = self.shift_y(y)

    def shift_x(self, x, y):
        if self.base_shift == 0:
            return x

        return SAMPLE_X + (x - SAMPLE_X) * (1 - self.shift_factor * (y - self.y_mid))

    def shift_y(self, y):
        return mod(y, PANORAMA_WIDTH-1)

    def original(self, x, y):
        return int(self.x[y, x]), int(self.y[y, x])


class Cliches:
    """
    A fixed set of Cliche's (see above) to sample panoramas with
    """
    all = []

    for angle in arange(0, PANORAMA_ANGLE, SAMPLE_ANGLE):
        left_top_x = SAMPLE_X
        right_bottom_x = SAMPLE_X + SAMPLE_HEIGHT
        left_top_y = angle * PANORAMA_WIDTH / PANORAMA_ANGLE
        right_bottom_y = left_top_y + SAMPLE_WIDTH

        x, y = meshgrid(arange(left_top_x, right_bottom_x, 1 / SAMPLE_MAGNIFICATION),
                        arange(left_top_y, right_bottom_y, 1 / SAMPLE_MAGNIFICATION))

        base_cliche = Cliche(x, y, 0, 1)
        all.append(base_cliche)

        for base_shift in SAMPLE_SHIFTS:
            for shift_direction in [1, -1]:
                all.append(Cliche(x, y, base_shift, shift_direction))
