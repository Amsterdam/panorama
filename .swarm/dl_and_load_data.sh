#!/usr/bin/env bash

_db_docker=`docker ps -q -f "name=panoswarm_database"`

docker exec $_db_docker /bin/update-table.sh panorama panoramas_region public panorama
docker exec $_db_docker /bin/update-table.sh panorama panoramas_panorama public panorama

