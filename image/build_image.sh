#!/usr/bin/env bash

docker build . -t build.datapunt.amsterdam.nl:5000/datapunt/python_opencv_openalpr
docker push build.datapunt.amsterdam.nl:5000/datapunt/python_opencv_openalpr