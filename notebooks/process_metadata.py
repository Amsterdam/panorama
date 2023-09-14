# Databricks notebook source
from processing import metadata

# COMMAND ----------

panos = metadata.read_panos("dbfs:/FileStore/tables/panorama/*/*/*/*/panorama1.csv")
panos.write.saveAsTable("dpbk_dev.panorama.bronze_panoramas")
miss = metadata.read_missiegegevens("dbfs:/FileStore/tables/panorama/*/missiegegevens.csv")
miss.write.saveAsTable("dpbk_dev.panorama.bronze_missions")

# COMMAND ----------

panos = spark.read.table("dpbk_dev.panorama.bronze_panoramas")
miss = spark.read.table("dpbk_dev.panorama.bronze_missions")

# COMMAND ----------

panos = metadata.make_api_table_panoramas(panos, miss)
panos.write.saveAsTable("dpbk_dev.panorama.silver_panoramas", partitionBy="mission_year")

# COMMAND ----------

panos = spark.read.table("dpbk_dev.panorama.silver_panoramas")

# COMMAND ----------

# MAGIC %sql
# MAGIC optimize dpbk_dev.panorama.silver_panoramas

# COMMAND ----------

miss = metadata.make_api_table_missions(miss)
miss.write.saveAsTable("dpbk_dev.panorama.silver_missions", partitionBy="mission_year")

# COMMAND ----------

# Save panoramas table as a single CSV for exporting to the API.

import gzip

with gzip.open("/dbfs/FileStore/tables/panorama/panos_for_api.csv.gz", "wb") as f:
    panos.toPandas().to_csv(f)
