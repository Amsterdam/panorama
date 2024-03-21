# Databricks notebook source
# MAGIC %md
# MAGIC This notebook handles the images from before 2023.

# COMMAND ----------

# MAGIC %pip install -r ../requirements.txt

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import kornia
import torch

from datetime import datetime
import os
import os.path

from processing.metadata import strip_filename
from processing.transform import cubic, equirectangular, _images


def process_row(row):
    filename = row["input_name"]
    try:
        process(filename, row["id"], row["heading"], row["pitch"], row["roll"])
    except Exception as e:
        return (filename, e, datetime.now())
    return (filename, None, datetime.now())


def process(filename: str, out_dir: str, heading: float, pitch: float, roll: float):
    im = _images.tensor_from_jpeg(open(filename, "rb").read())

    dirs_made = set()  # Directories that we made (or found out exist).

    for filename, im in _process(im, heading, pitch, roll):
        jpg = _images.jpeg_from_tensor(im)
        filename = os.path.join(out_dir, filename)

        d = os.path.dirname(filename)
        if d not in dirs_made:
            os.makedirs(d, exist_ok=True)
            while True:
                dirs_made.add(d)
                d = os.path.dirname(d)
                if d in dirs_made:
                    break

        with open(filename, "wb") as f:
            f.write(jpg)


def _process(im, heading, pitch, roll):
    # Make equirectangular parts.
    im = im.to(torch.float32)
    im = equirectangular.rotate(im, heading, pitch, roll, target_width=8000)

    yield "equirectangular/panorama_8000.jpg", im
    yield "equirectangular/panorama_4000.jpg", _images.resize(im, 4000)
    yield "equirectangular/panorama_2000.jpg", _images.resize(im, 2000)

    # Make cubic parts and prepend "cubic/".
    for name, part in cubic.make_fileset(cubic.project(im)):
        yield os.path.join("cubic", name), part

# COMMAND ----------

from glob import glob

all_files = glob("/Volumes/DPBK_DEV/default/landingzone_panoramas/*/2022/*/*/*/*.jpg")

# COMMAND ----------

out_dir = "/Volumes/DPBK_PRD/default/panorama"

todo = spark.createDataFrame(
    sc.parallelize(all_files).map(lambda name: (name, out_dir + "/" + strip_filename(name))),
    schema=["input_name", "id"],
)

# COMMAND ----------

# Get the heading, roll and pitch from the metadata table and join with the filenames.
# Constructing the entire output directory name for the key is the easiest option.

from processing import metadata

meta_old = spark.sql(f"""
    select
        concat_ws('/', '{out_dir}', year, format_string("%02d", month), format_string("%02d", day), mission, panorama_file_name) as id,
        `heading[deg]` as heading, `roll[deg]` as roll, `pitch[deg]` as pitch
    from
        dpbk_dev.panorama.bronze_panoramas_old
""")

# COMMAND ----------

# TODO: filter away pictures from spark.read.table("dpbk_dev.panorama.silver_pictures_processed")
todo = todo.join(meta_old, "id")

# COMMAND ----------

r = todo.rdd.map(process_row)

# COMMAND ----------

r.collect()

# COMMAND ----------

ok = spark.createDataFrame([(filename, t) for filename, exc, t in r if exc is None], schema=["filename"])
ok.write.mode("append").saveAsTable("dpbk_dev.panorama.silver_pictures_processed")
