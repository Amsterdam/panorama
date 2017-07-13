#!/usr/bin/env bash

if [ -f /home/archive/exported_regions.dmp ]; then
	_now=$(date +"%Y%m%dT%H%M")
	mv /home/archive/exported_regions.dmp /home/archive/exported_regions_$_now.dmp
fi

_db_docker=`docker ps -q -f "name=panoswarm_database"`

docker exec -it $_db_docker .dmp -U panorama -c 'drop table if exists region_export'
docker exec -it $_db_docker .dmp -U panorama -c 'create table region_export as select region_type, left_top_x, left_top_y, right_top_x, right_top_y, left_bottom_x, left_bottom_y, right_bottom_x, right_bottom_y, detected_by, pano_id from panoramas_region'
docker exec -it $_db_docker pg_dump -Fc -t region_export* -d panorama -U panorama -f /tmp/exported_regions.dmp
docker cp $_db_docker:/tmp/exported_regions.dmp /home/archive/exported_regions.dmp
