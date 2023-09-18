# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

images = spark.read.format("binaryFile").load("dbfs:/FileStore/tables/panorama/*/*/*/*/pano_????_??????.jpg")

# COMMAND ----------

# Construct a pano_id from the last two parts of the path, with .jpg stripped off.
# TODO: the indices 7 and 8 depend on the exact path layout. Fix that.
images = images.selectExpr("split(path, '/')[7] as pid1", "split(path, '/')[8] as pid2", "content")
images = images.selectExpr("format_string('%s_%s', pid1, split(pid2, '.jpg')[0]) as pano_id", "content")

# COMMAND ----------

meta = spark.read.table("dpbk_dev.panorama.silver_panoramas")

# COMMAND ----------

# Should produce a DF with pano_id, content, roll, pitch, heading.
images = images.join(meta, "pano_id").select("pano_id", "content", "roll", "pitch", "heading")
