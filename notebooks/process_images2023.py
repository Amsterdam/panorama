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

from datetime import datetime
import os
import os.path

from processing.metadata import strip_filename
from processing.transform import cubic, _images


def run(filename):
    try:
        process(filename, out_dir="/Volumes/DPBK_PRD/default/panorama")
    except Exception as e:
        return (filename, e, datetime.now())
    return (filename, None, datetime.now())


def process(filename: str, out_dir: str):
    out_dir = os.path.join(out_dir, strip_filename(filename))
    im = _images.tensor_from_jpeg(open(filename, "rb").read())

    dirs_made = set()  # Directories that we made (or found out exist).

    for filename, im in _process(im):
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

# Find all input pictures.
all_files = glob("/Volumes/DPBK_DEV/default/landingzone_panoramas/2023-11-29_17_42_40/intermediate/2023/*/*/*/*.jpg")
len(all_files)

# COMMAND ----------

# Remove panoramas that are listed as done. We need to update this table later.
done = sql("select * from dpbk_dev.panorama.silver_pictures_processed")
done = {row["filename"] for row in done.collect()}

todo = [f for f in all_files if f not in done]
len(todo)  # Should eventually become 0.

# COMMAND ----------

# Smaller batch, for testing changes etc.
# todo = todo[:5000]

# COMMAND ----------

# Process images. Calling collect forces a wait for the result.
#
# Use the maximum number of partitions. The work per picture is multiple seconds and
# the transient EACCESS errors greatly skew the distribution of work across partitions.
r = sc.parallelize(todo, len(todo)).map(run).collect()

# Check which images were successfully processed and add those to the delta table.
# (Trying to convert an RDD to a DataFrame directly runs into some permission issue,
# so do this on the master node.)
ok = spark.createDataFrame([(filename, t) for filename, exc, t in r if exc is None], schema=["filename"])
ok.write.mode("append").saveAsTable("dpbk_dev.panorama.silver_pictures_processed")
ok.count()

# COMMAND ----------

# We tend to get lots of "permission denied" errors, which are apparently all transient,
# so keep retrying the few cells above until everything's done.
failed = [filename for filename, exc, _ in r if exc is not None]
len(failed)  # Should eventually become zero.
