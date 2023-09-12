Panorama processing
===================

This project contains code for processing panorama images for display in the
web-based viewer at https://data.amsterdam.nl, and for preparing a database of
metadata served by the [Panorama API](https://github.com/Amsterdam/panorama-api).
Images are oriented and cubically projected.

All the code in this repo is written to run on the Databricks platform.
Its expected input is panorama images in JPEG format + CSV files containing
metadata. Blurring of faces and license plates is assumed to have already been
done (by the Computer Vision Team).
