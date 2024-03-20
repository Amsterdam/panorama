# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC Optimize input images with jpegoptim.
# MAGIC
# MAGIC The images coming from the blurring pipeline are bigger than they could be, by about 14%.
# MAGIC This notebook runs jpegoptim on them to save space.

# COMMAND ----------

# Should match directories containing images to optimize (not the image files themselves!).
# The result will be a CSV file per directory in csv_dir, so directory names must be unique.
pattern = "/Volumes/DPBK_DEV/default/landingzone_panoramas/*/20??/*/*/*"

csv_dir = "/Volumes/DPBK_DEV/default/landingzone_panoramas/jpegoptim

# COMMAND ----------

from glob import glob
import os.path
import shutil
from subprocess import Popen
import subprocess
from tempfile import TemporaryDirectory


def optimize(d):
    base = os.path.basename(d)
    csv = os.path.join(csv_dir, base)

    with TemporaryDirectory(dir="/dev/shm", prefix="jpegoptim-") as tmp:
        with open(csv, "wb") as stdout:
            subprocess.run(
                ["jpegoptim", "-d", tmp, "--csv"] + glob(d + "/*.jpg"),
                stdout=stdout,
            )
            for f in glob(tmp + "/*.jpg"):
                shutil.move(f, d + "/" + os.path.basename(f))

# COMMAND ----------

dirs = glob(pattern)
dirs = sc.parallelize(dirs, len(dirs))
dirs.foreach(optimize)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC -- See how much we saved, in GB.
# MAGIC select sum(_c4 -_c5) / (1024 * 1024 * 1024) from csv.`/Volumes/DPBK_DEV/default/landingzone_panoramas/jpegoptim/*`
