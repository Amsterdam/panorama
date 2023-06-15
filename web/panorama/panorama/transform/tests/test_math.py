from math import sqrt
import panorama.transform.utils_math_array as Math
from numpy.testing import assert_allclose, assert_array_equal


def test_cylindrical2cartesion():
    result = Math.cylindrical2cartesian((4000, 2000), 8000, 4000)
    assert_allclose(result, [1, 0, 0], atol=1e-15)

    result = Math.cylindrical2cartesian((2000, 2000), 8000, 4000)
    assert_allclose(result, [0, -1, 0], atol=1e-15)

    result = Math.cylindrical2cartesian((0, 2000), 8000, 4000)
    assert_allclose(result, [-1, 0, 0], atol=1e-15)

    result = Math.cylindrical2cartesian((6000, 2000), 8000, 4000)
    assert_allclose(result, [0, 1, 0], atol=1e-15)

    result = Math.cylindrical2cartesian((4000, 1000), 8000, 4000)
    assert_allclose(result, [sqrt(1 / 2), 0, sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((4000, 3000), 8000, 4000)
    assert_allclose(result, [sqrt(1 / 2), 0, -sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((2000, 1000), 8000, 4000)
    assert_allclose(result, [0, -sqrt(1 / 2), sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((2000, 3000), 8000, 4000)
    assert_allclose(result, [0, -sqrt(1 / 2), -sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((0, 1000), 8000, 4000)
    assert_allclose(result, [-sqrt(1 / 2), 0, sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((0, 3000), 8000, 4000)
    assert_allclose(result, [-sqrt(1 / 2), 0, -sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((6000, 1000), 8000, 4000)
    assert_allclose(result, [0, sqrt(1 / 2), sqrt(1 / 2)], atol=1e-15)

    result = Math.cylindrical2cartesian((6000, 3000), 8000, 4000)
    assert_allclose(result, [0, sqrt(1 / 2), -sqrt(1 / 2)], atol=1e-15)


def test_cartesian2cylindrical():
    result = Math.cartesian2cylindrical((1, 0, 0), 8000, 4000)
    assert_allclose(result, [4000, 2000], atol=1e-15)

    result = Math.cartesian2cylindrical((0, -1, 0), 8000, 4000)
    assert_allclose(result, [2000, 2000], atol=1e-15)

    result = Math.cartesian2cylindrical((-1, 0, 0), 8000, 4000)
    assert_allclose(result, [1, 2000], atol=1e-15)

    result = Math.cartesian2cylindrical((0, 1, 0), 8000, 4000)
    assert_allclose(result, [6000, 2000], atol=1e-15)

    result = Math.cartesian2cylindrical((sqrt(1 / 2), 0, sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [4000, 1000], atol=1e-15)

    result = Math.cartesian2cylindrical((sqrt(1 / 2), 0, -sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [4000, 3000], atol=1e-15)

    result = Math.cartesian2cylindrical((0, -sqrt(1 / 2), sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [2000, 1000], atol=1e-15)

    result = Math.cartesian2cylindrical((0, -sqrt(1 / 2), -sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [2000, 3000], atol=1e-15)

    result = Math.cartesian2cylindrical((-sqrt(1 / 2), 0, sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [1, 1000], atol=1e-15)

    result = Math.cartesian2cylindrical((-sqrt(1 / 2), 0, -sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [1, 3000], atol=1e-15)

    result = Math.cartesian2cylindrical((0, sqrt(1 / 2), sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [6000, 1000], atol=1e-15)

    result = Math.cartesian2cylindrical((0, sqrt(1 / 2), -sqrt(1 / 2)), 8000, 4000)
    assert_allclose(result, [6000, 3000], atol=1e-15)


def test_rotation_matrix():
    result = Math.rotation_matrix(0, 0, 0)
    assert_array_equal(result, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    result = Math.rotation_matrix(90, 0, 0)
    assert_allclose(result, [[0, 1, 0], [-1, 0, 0], [0, 0, 1]], atol=1e-15)

    result = Math.rotation_matrix(-90, 0, 0)
    assert_allclose(result, [[0, -1, 0], [1, 0, 0], [0, 0, 1]], atol=1e-15)

    result = Math.rotation_matrix(0, 90, 0)
    assert_allclose(result, [[0, 0, 1], [0, 1, 0], [-1, 0, 0]], atol=1e-15)

    result = Math.rotation_matrix(0, 45, 45)
    assert_allclose(
        result,
        [
            [sqrt(1 / 2), 0, sqrt(1 / 2)],
            [1 / 2, sqrt(1 / 2), -1 / 2],
            [-1 / 2, sqrt(1 / 2), 1 / 2],
        ],
        atol=1e-15,
    )
