from datetime import datetime

import pandas as pd
import pytest

from . import _from_gps_time


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
