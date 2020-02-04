#!/usr/bin/env bash

ARCHIVE_PATH=~/archive

if [ ! -d  $ARCHIVE_PATH ]; then
	mkdir $ARCHIVE_PATH
fi

if [ -f $ARCHIVE_PATH/exported_regions.dmp ]; then
	_now=$(date +"%Y%m%dT%H%M")
	mv $ARCHIVE_PATH/exported_regions.dmp $ARCHIVE_PATH/exported_regions_$_now.dmp
fi

_db_docker=`docker ps -q -f "name=panoswarm_database"`

docker exec $_db_docker psql -U panorama -c 'drop table if exists region_export'
docker exec $_db_docker psql -U panorama -c 'create table region_export as select region_type, left_top_x, left_top_y, right_top_x, right_top_y, left_bottom_x, left_bottom_y, right_bottom_x, right_bottom_y, detected_by, pano_id from panoramas_region'
docker exec $_db_docker pg_dump -Fc -t region_export* -d panorama -U panorama -f /tmp/exported_regions.dmp
docker cp $_db_docker:/tmp/exported_regions.dmp /tmp/exported_regions.dmp
cp /tmp/exported_regions.dmp $ARCHIVE_PATH/exported_regions.dmp
