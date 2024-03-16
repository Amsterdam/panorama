import pandas as pd
import pytest

from . import (
    _from_gps_time,
    _make_pointz,
    _normalize_panos_kavel10,
    read_missiegegevens,
    read_panos_old,
    read_panos_kavel10,
)


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


def test_read_and_join(spark):
    miss = read_missiegegevens(
        spark, "processing/transform/testdata/*/missiegegevens.csv"
    )
    assert set(miss.columns) == {
        "mission",
        "water/land",
        "week",
        "datum",
        "neighbourhood",
        "Naar ftp",
        "mission_distance",
        "mission_type",
        "woz-jaargang",
        "surface_type",
        "mission_year",
    }

    panos_old = read_panos_old(
        spark, "processing/transform/testdata/*/*/*/*/panorama1.csv"
    )
    assert set(panos_old.columns) == {
        "gps_seconds[s]",
        "panorama_file_name",
        "latitude[deg]",
        "longitude[deg]",
        "altitude_ellipsoidal[m]",
        "roll[deg]",
        "pitch[deg]",
        "heading[deg]",
        "dirname",
        "year",
        "month",
        "day",
        "mission",
    }

    panos_k10 = read_panos_kavel10(
        spark, "processing/transform/testdata/2023/11/16/Bravo_MOSAIC_Merged.mxeo"
    )
    panos_k10 = _normalize_panos_kavel10(panos_k10)
    # TODO make this work:
    # assert panos_k10.columns == panos_old.columns
