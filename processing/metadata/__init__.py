"""Metadata processing code.

See ../../notebooks/process_metadata.py for usage.
"""

from typing import Iterator

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from ._filenames import strip_filename


def make_api_table_missions(df: DataFrame) -> DataFrame:
    """Convert result of read_missiegegevens to the table panoramas_missions."""
    df = df.withColumnRenamed("mission", "name")
    df = df.withColumn("date", F.to_date("datum", "d-M-y"))
    return df.select(
        "name",
        "date",
        "neighbourhood",
        "mission_type",
        "mission_year",
        "surface_type",
        "mission_distance",
    )


def make_api_table_panoramas(panos: DataFrame, missions: DataFrame) -> DataFrame:
    """Make panoramas_panorama table for the API.

    This produces all columns except for id, and _geolocation_2d_rd is null.
    """
    panos = _prepare_panos_for_join(panos)
    df = panos.join(missions, "mission")

    month = F.format_string("%02d", "month")
    day = F.format_string("%02d", "day")
    df = df.withColumn(
        "path",
        # Path column always has a trailing slash.
        F.concat(F.concat_ws("/", "year", month, day, "mission"), F.lit("/")),
    )

    # Add the array column "tags".
    df = df.withColumn(
        "tags",
        F.array_compact(
            F.array(
                F.concat(F.lit("mission-"), "mission_type"),
                F.concat(F.lit("mission-"), "mission_year"),
                F.concat(F.lit("mission-distance-"), "mission_distance"),
                F.concat(F.lit("surface-"), "water/land"),
            )
        ),
    )

    return df.select(
        "pano_id",
        "timestamp",
        "filename",
        "path",
        "geolocation",
        "roll",
        "pitch",
        "heading",
        "_geolocation_2d",
        "status",
        "status_changed",
        "mission_type",
        "_geolocation_2d_rd",
        "mission_year",
        "surface_type",
        "mission_distance",
        "tags",
    )


def _prepare_panos_for_join(df: DataFrame) -> DataFrame:
    """Prepare panos DataFrame for joining with missions."""

    @F.pandas_udf("timestamp")
    def from_gps_time(it: Iterator[pd.Series]) -> Iterator[pd.Series]:
        return _from_gps_time(it)

    df = df.withColumn("pano_id", F.concat_ws("_", "mission", "panorama_file_name"))
    df = df.withColumn("timestamp", from_gps_time("gps_seconds[s]"))
    df = df.withColumn("filename", F.concat("panorama_file_name", F.lit(".jpg")))

    geolocation = _make_pointz(
        "longitude[deg]",
        "latitude[deg]",
        "altitude_ellipsoidal[m]",
    )
    df = df.withColumn("geolocation", geolocation)
    space = F.lit(" ")
    geolocation = F.concat(
        F.lit("POINT("), "longitude[deg]", space, "latitude[deg]", F.lit(")")
    )
    df = df.withColumn("_geolocation_2d", geolocation)
    # _geolocation_2d_rd will hold the EPSG:28992 version of _geolocation_2d.
    # We'll compute this in Postgres, so leave it null for now.
    df = df.withColumn("_geolocation_2d_rd", F.lit(None))

    for col in ["roll", "pitch", "heading"]:
        df = df.withColumnRenamed(col + "[deg]", col)

    # The status and status_changed columns refer to a previous version
    # where the database was used as a work queue. They're meaningless,
    # but fill them in anyway as the API may still rely on them.
    df = df.withColumns(
        {"status": F.lit("done"), "status_changed": F.current_timestamp()}
    )
    return df


def read_missiegegevens(spark: SparkSession, path: str) -> DataFrame:
    """Read the missiegegevens file.

    This file contains information about missions. It is constructed by
    DataOffice.
    """
    schema = StructType(
        [
            StructField("Missienaam", StringType(), False),
            StructField("water/land", StringType(), False),
            StructField("week", StringType(), True),
            StructField("datum", StringType(), False),
            StructField("Gebied", StringType(), False),
            StructField("Naar ftp", StringType(), False),
            StructField("rijafstand", IntegerType(), False),
            StructField("missietype", StringType(), False),
            StructField("woz-jaargang", StringType(), True),
        ]
    )

    df = spark.read.csv(path, schema=schema, sep="\t", header=True)

    for old, new in [
        ("Gebied", "neighbourhood"),
        ("Missienaam", "mission"),  # For join with panos.
        ("missietype", "mission_type"),
        ("rijafstand", "mission_distance"),
    ]:
        df = df.withColumnRenamed(old, new)

    df = df.withColumn("surface_type", F.upper(F.substring("water/land", 1, 1)))

    df = df.withColumn(
        "mission_year",
        F.coalesce(F.col("woz-jaargang"), F.year(F.to_date("datum", "d-M-y"))),
    )

    return df


def read_panos_old(spark: SparkSession, path: str) -> DataFrame:
    """Reads all the panorama1.csv files from path.

    The path should be a glob pattern, say "somewhere/*/*/*/*/panorama1.csv".
    The four asterisks are interpreted as year, month, day, mission dirs.
    """
    schema = StructType(
        [
            StructField("gps_seconds[s]", DoubleType(), False),
            StructField("panorama_file_name", StringType(), False),
            StructField("latitude[deg]", DoubleType(), False),
            StructField("longitude[deg]", DoubleType(), False),
            StructField("altitude_ellipsoidal[m]", DoubleType(), False),
            StructField("roll[deg]", DoubleType(), False),
            StructField("pitch[deg]", DoubleType(), False),
            StructField("heading[deg]", DoubleType(), False),
        ]
    )

    df = spark.read.csv(path, schema=schema, sep="\t", header=True)
    df = _parse_dates_from_filenames(df)
    return df


def read_panos_kavel10(spark: SparkSession, path: str) -> DataFrame:
    """Read Kavel 10's metadata files."""
    schema = StructType(
        [
            StructField("ImageName", StringType(), True),
            StructField("UTC_Date_Time", StringType(), True),
            StructField("GPS_Week_Seconds", DoubleType(), True),
            StructField("X", DoubleType(), True),
            StructField("Y", DoubleType(), True),
            StructField("Z", DoubleType(), True),
            StructField("Time", StringType(), True),
            StructField("Date", StringType(), True),
            StructField("Roll", DoubleType(), True),
            StructField("Pitch", DoubleType(), True),
            StructField("Heading", DoubleType(), True),
            StructField("Vel_North", DoubleType(), True),
            StructField("Vel_East", DoubleType(), True),
            StructField("Vel_Up", DoubleType(), True),
            StructField("Vel_Down", DoubleType(), True),
            StructField("RMS_North", DoubleType(), True),
            StructField("RMS East", DoubleType(), True),
            StructField("RMS_Elevation", DoubleType(), True),
            StructField("RMS_Roll", DoubleType(), True),
            StructField("RMS_Pitch", DoubleType(), True),
            StructField("RMS_Heading", DoubleType(), True),
        ]
    )

    df = spark.read.csv(path, schema=schema, header=True)
    df = _parse_dates_from_filenames(df)
    return df


def _normalize_panos_kavel10(df: DataFrame):
    """Transform Kavel10 metadata to something closer to our old format."""
    # ImageName is the base filename, including ".jpg".
    df = df.withColumnRenamed("ImageName", "panorama_file_name")

    df = df.withColumn("pano_id", F.expr("substring(panorama_file_name, 1, len(panorama_file_name) - 4)"))

    # UTC_Date_Time is ${date}_${time}, but with the leading digits
    # of the year missing. Assume it's the 21st century for now.
    df = df.withColumn(
        "timestamp",
        F.expr(
            """from_utc_timestamp(
                concat('20', replace(UTC_Date_Time, '_', 'T')),
                'Europe/Amsterdam'
            )
            """
        ),
    )

    # TODO X and Y are RD coordinates. Convert.
    df = df.withColumn("geolocation", _make_pointz("X", "Y", "Z"))

    for col in ["Roll", "Pitch", "Heading"]:
        df = df.withColumnRenamed(col, col.lower())

    return df.select(
        "panorama_file_name",
        "timestamp",
        "geolocation",
        "roll",
        "pitch",
        "heading",
    )


def read_trajectories(
    spark: SparkSession,
    path: str = "/tmp/testdata/*/*/*/*/trajectory.csv",
) -> DataFrame:
    schema = StructType(
        [
            StructField("gps_seconds[s]", DoubleType(), False),
            StructField("latitude[deg]", DoubleType(), False),
            StructField("longitude[deg]", DoubleType(), False),
            StructField("altitude_ellipsoidal[m]", DoubleType(), False),
            StructField("north_rms[m]", DoubleType(), False),
            StructField("east_rms[m]", DoubleType(), False),
            StructField("down_rms[m]", DoubleType(), False),
            StructField("roll_rms[deg]", DoubleType(), False),
            StructField("pitch_rms[deg]", DoubleType(), False),
            StructField("heading_rms[deg]", DoubleType(), False),
        ]
    )

    df = spark.read.csv(path, schema=schema, sep="\t", header=True)
    df = _parse_dates_from_filenames(df)
    return df


def _parse_dates_from_filenames(df: DataFrame) -> DataFrame:
    """Parse year, month, day and mission from df's filenames
    and add them as columns.
    """
    # All columns we add, including the temporary one.
    cols = ["_filename", "dirname", "year", "month", "day", "mission"]
    for col in cols:
        if col in df.columns:
            raise ValueError(f"{col!r} already in use")

    df = df.withColumn("_filename", F.input_file_name())
    df = df.withColumn("_filename", F.split("_filename", "/"))
    dirname = F.array_join(F.slice("_filename", 1, F.size("_filename") - 1), "/")
    df = df.withColumn("dirname", dirname)

    df = df.withColumn("_filename", F.expr("slice(_filename, -5, 4)"))

    for i, col in enumerate(["year", "month", "day"]):
        df = df.withColumn(col, F.expr(f"cast(_filename[{i}] as int)"))
    df = df.withColumn("mission", F.expr("_filename[3]"))

    return df.drop("_filename")


def _from_gps_time(it: Iterator[pd.Series]) -> Iterator[pd.Series]:
    """Convert GPS timestamps to datetimes.

    Only valid for timestamps after 2015-07-01. Earlier times will be off by
    a few seconds due to lack of leap seconds.
    """
    # UTC offset for dates after 2015-07-01, including the 17 leap seconds
    # since the GPS epoch (1980).
    UTC_FROM_GPS = 315964800 - 17
    # UTC timestamps of leap seconds after 2015-07-01.
    leap_seconds = sorted([1483228800], reverse=True)

    for t in it:
        t = t + UTC_FROM_GPS
        for leap in leap_seconds:
            t -= t > leap
        yield pd.to_datetime(t, unit="s", utc=True)


def _make_pointz(x, y, z):
    space = F.lit(" ")
    return F.concat(F.lit("POINT Z("), x, space, y, space, z, F.lit(")"))
