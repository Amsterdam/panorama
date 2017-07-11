#!/usr/bin/env bash

_now=$(date +"%Y%m%dT%H%M")
mv /tmp/exported_regions.sql /tmp/exported_regions_$_now.sql

_db_docker=`docker ps -q -f "name=panoswarm_database"`

echo EXPORTING DATA FROM CONTAINTER $_db_docker

docker exec -it $_db_docker psql -U panorama -c 'create table region_export as select region_type, left_top_x, left_top_y, right_top_x, right_top_y, left_bottom_x, left_bottom_y, right_bottom_x, right_bottom_y, detected_by, pano_id from panoramas_region'
docker exec -it $_db_docker pg_dump -Fc -t region_export* -d panorama -U panorama -f /tmp/exported_regions.sql
docker cp $_db_docker:/tmp/exported_regions.sql /tmp/