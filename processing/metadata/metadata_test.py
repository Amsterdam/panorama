import pandas as pd
import pytest

from . import _from_gps_time, _make_pointz


@pytest.mark.parametrize(
    ("gps", "utc"),
    [
        (1125910500, "2015-09-10T08:54:43+00:00"),
        (1360069949, "2023-02-10T13:12:11+00:00"),
    ],
)
def test_from_gps_time(gps, utc):
    from_gps = next(_from_gps_time([pd.Series([gps])]))
    assert from_gps[0].isoformat() == utc


def test_make_pointz(spark):
    df = spark.createDataFrame([{"x": 1.1, "y": 2.2, "z": 3.3}])
    pointz = df.select(_make_pointz(df.x, df.y, df.z)).collect()[0][0]
    assert pointz == "POINT Z(1.1 2.2 3.3)"
