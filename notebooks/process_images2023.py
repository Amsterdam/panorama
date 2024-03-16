# Databricks notebook source
# This notebook handles the images from 2023, which are special in that they
# don't need rotating. That's because the unrotated images went missing, so
# blurring was done on the rotated images instead.

# COMMAND ----------

# MAGIC %pip install -r ../requirements.txt

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import kornia
import torch

import os
import os.path

from processing.transform import cubic, _images


def run(filename):
    """Returns (filename, exception), or None if no exception was raised."""
    try:
        process(filename, out_dir="/Volumes/DPBK_PRD/default/panorama")
    except Exception as e:
        return (filename, e)
    return (filename, None)


def process(filename: str, out_dir: str):
    out_dir = os.path.join(out_dir, _parse_filename(filename))
    im = _images.tensor_from_jpeg(open(filename, "rb").read())

    for filename, im in _process(im):
        jpg = _images.jpeg_from_tensor(im)
        filename = os.path.join(out_dir, filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(jpg)


def _parse_filename(filename: str) -> str:
    orig = filename
    dirname, filename = os.path.split(filename)
    filename, jpg = os.path.splitext(filename)
    if jpg.lower() != ".jpg":
        raise ValueError(f"expected a filename ending in .jpg, got {filename!r}")

    dirname, mission = os.path.split(dirname)
    dirname, day = os.path.split(dirname)
    dirname, month = os.path.split(dirname)
    dirname, year = os.path.split(dirname)
    if not all([day, dirname, filename, month, mission, year]):
        raise ValueError(f"unexpected path {orig!r}")

    return os.path.join(year, month, day, mission, filename)


def _process(im):
    # Make equirectangular parts, which for 2023 means just resizing.
    yield "equirectangular/panorama_8000.jpg", im
    im = im.to(torch.float32)
    yield "equirectangular/panorama_4000.jpg", _images.resize(im, 4000)
    yield "equirectangular/panorama_2000.jpg", _images.resize(im, 2000)

    # Make cubic parts and prepend "cubic/".
    for name, part in cubic.make_fileset(cubic.project(im)):
        yield os.path.join("cubic", name), part

# COMMAND ----------

from glob import glob

input_dir = "/Volumes/DPBK_DEV/default/panoramas_input/2023-11-29_17_42_40/intermediate/"

todo = glob(input_dir + "2023/01/*/*/*.jpg")

# Remove panoramas that are listed as done. We need to update this table later.
done = sql("select * from dpbk_dev.panorama.silver_pictures_processed")
done = {row["filename"] for row in done.collect()}

todo = [f for f in todo if f not in done]
len(todo)

# COMMAND ----------

# Process images. Calling collect forces a wait for the result.
r = sc.parallelize(todo).map(run).collect()

# Check which images were successfully processed and add those to the delta table.
ok = spark.createDataFrame([(filename,) for filename, exc in r if exc is None], schema=["filename"])
ok.write.mode("append").saveAsTable("dpbk_dev.panorama.silver_pictures_processed")
ok.count()

# COMMAND ----------

# We tend to get lots of "permission denied" errors, which are apparently all transient,
# so keep retrying the previous cell until everything's done.
todo = [filename for filename, exc in r if exc is not None]
len(todo)  # Should eventually become zero.
