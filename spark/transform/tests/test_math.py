from math import sqrt

import torch
from torch.testing import assert_close

from .. import _math


def test_cartesian_from_cylindrical():
    # Simple test against what the old NumPy implementation produced.
    result = _math.cartesian_from_cylindrical(torch.arange(4), torch.arange(3))
    expect_x = torch.tensor(
        [
            [0, 0, 0, 0],
            [-0.866025404, 5.30287619e-17, 0.866025404, 5.30287619e-17],
            [-0.866025404, 5.30287619e-17, 0.866025404, 5.30287619e-17],
        ],
        dtype=torch.float32,
    )
    expect_y = torch.tensor(
        [
            [0, 0, 0, 0],
            [-1.06057524e-16, -0.866025404, 0, 0.866025404],
            [-1.06057524e-16, -0.866025404, 0, 0.866025404],
        ],
        dtype=torch.float32,
    )
    expect_z = torch.tensor(
        [[1, 1, 1, 1], [0.5, 0.5, 0.5, 0.5], [-0.5, -0.5, -0.5, -0.5]],
        dtype=torch.float32,
    )

    assert_close(result[0], expect_x, check_dtype=True)
    assert_close(result[1], expect_y, check_dtype=True)
    assert_close(result[2], expect_z, check_dtype=True)


def test_cylindrical_from_cartesian():
    data = torch.tensor(
        [
            [1, 0, 0, 4000, 2000],
            [0, -1, 0, 2000, 2000],
            [-1, 0, 0, 0, 2000],
            [0, 1, 0, 6000, 2000],
            [sqrt(0.5), 0, sqrt(0.5), 4000, 1000],
            [sqrt(0.5), 0, -sqrt(0.5), 4000, 3000],
            [0, -sqrt(0.5), sqrt(0.5), 2000, 1000],
            [0, -sqrt(0.5), -sqrt(0.5), 2000, 3000],
            [-sqrt(0.5), 0, sqrt(0.5), 0, 1000],
            [-sqrt(0.5), 0, -sqrt(0.5), 0, 3000],
            [0, sqrt(0.5), sqrt(0.5), 6000, 1000],
            [0, sqrt(0.5), -sqrt(0.5), 6000, 3000],
        ],
        dtype=torch.float32,
    )

    x, y, z = data[:, 0], data[:, 1], data[:, 2]
    x, y = _math.cylindrical_from_cartesian(x, y, z, 8000, 4000)

    assert_close(x, data[:, 3], atol=1e-15, rtol=0)
    assert_close(y, data[:, 4], atol=1e-15, rtol=0)


def test_rotation_matrix():
    result = _math.rotation_matrix(0, 0, 0)
    assert_close(result, torch.eye(3), atol=0, rtol=0)

    def t(x):
        return torch.tensor(x, dtype=torch.float32)

    result = _math.rotation_matrix(90, 0, 0)
    expect = t([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    assert_close(result, expect, atol=1e-15, rtol=0)

    result = _math.rotation_matrix(-90, 0, 0)
    expect = t([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    assert_close(result, expect, atol=1e-15, rtol=0)

    result = _math.rotation_matrix(0, 90, 0)
    expect = t([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
    assert_close(result, expect, atol=1e-15, rtol=0)

    result = _math.rotation_matrix(0, 45, 45)
    expect = t(
        [
            [sqrt(1 / 2), 0, sqrt(1 / 2)],
            [1 / 2, sqrt(1 / 2), -1 / 2],
            [-1 / 2, sqrt(1 / 2), 1 / 2],
        ]
    )
    assert_close(result, expect, atol=1e-15, rtol=0)
