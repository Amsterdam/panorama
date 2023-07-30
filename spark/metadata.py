from typing import Union

from pyspark.sql import SparkSession
from pyspark.sql.column import Column
from pyspark.sql.dataframe import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

spark = SparkSession.builder.getOrCreate()


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
    df = df.withColumn("pano_id", F.concat_ws("_", "mission", "panorama_file_name"))
    df = df.withColumn("timestamp", _from_gps_time("gps_seconds[s]"))
    df = df.withColumn("filename", F.concat("panorama_file_name", F.lit(".jpg")))

    space = F.lit(" ")
    geolocation = F.concat(
        F.lit("POINT Z("),
        "longitude[deg]",
        space,
        "latitude[deg]",
        space,
        "altitude_ellipsoidal[m]",
        F.lit(")"),
    )
    df = df.withColumn("geolocation", geolocation)
    geolocation = F.concat(
        F.lit("POINT("), "longitude[deg]", space, "latitude[deg]", F.lit(")")
    )
    df = df.withColumn("_geolocation_2d", geolocation)
    # _geolocation_2d_rd will hold the EPSG:28992 version of _geolocation_2d.
    # We'll compute this in Postgres, so leave it null for now.
    df = df.withColumn("_geolocation_2d_rd", F.lit(None))

    df = df.withColumnsRenamed(
        {col + "[deg]": col for col in ["roll", "pitch", "heading"]}
    )

    # The status and status_changed columns refer to a previous version
    # where the database was used as a work queue. They're meaningless,
    # but fill them in anyway as the API may still rely on them.
    df = df.withColumns(
        {"status": F.lit("done"), "status_changed": F.current_timestamp()}
    )
    return df


def read_missiegegevens(path="/tmp/testdata/*/missiegegevens.csv") -> DataFrame:
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

    df = df.withColumnsRenamed(
        {
            "Gebied": "neighbourhood",
            "Missienaam": "mission",  # For join with panos.
            "missietype": "mission_type",
            "rijafstand": "mission_distance",
        }
    )

    df = df.withColumn("surface_type", F.upper(F.substring("water/land", 1, 1)))

    df = df.withColumn(
        "mission_year",
        F.coalesce(F.col("woz-jaargang"), F.year(F.to_date("datum", "d-M-y"))),
    )

    return df


def read_panos(path="/tmp/testdata/*/*/*/*/panorama1.csv") -> DataFrame:
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


def read_trajectories(path="/tmp/testdata/*/*/*/*/trajectory.csv") -> DataFrame:
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


def _from_gps_time(col: Union[str, Column]) -> Column:
    """Returns an expression that converts col from GPS time to timestamp.

    This only works for dates past 2015-07-01.
    """
    # UTC offset for dates after 2015-07-01, including the 17 leap seconds
    # since the GPS epoch (1980).
    UTC_FROM_GPS = 315964800 - 17
    # UTC timestamps of leap seconds after 2015-07-01.
    LEAP_SECONDS_INTRODUCED = [1483228800]

    if isinstance(col, str):
        col = F.col(col)

    col = col + F.lit(UTC_FROM_GPS).cast("double")
    for leap in sorted(LEAP_SECONDS_INTRODUCED, reverse=True):
        col = col - (col > F.lit(leap)).cast("double")

    return F.timestamp_seconds(col)
