#!/usr/bin/env bash

_db_docker=`docker ps -q -f "name=panoswarm_database"`

docker exec -it $_db_docker /bin/update-table.sh panorama panoramas_region public panorama
docker exec -it $_db_docker /bin/update-table.sh panorama panoramas_panorama public panorama

