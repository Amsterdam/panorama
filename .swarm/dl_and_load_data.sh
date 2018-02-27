#!/usr/bin/env bash

_db_docker=`docker ps -q -f "name=panoswarm_database"`

docker exec $_db_docker /bin/download-db.sh panorama
docker exec $_db_docker /bin/update-table.sh panorama panoramas_region public panorama
docker exec $_db_docker psql -U panorama -c 'delete from panoramas_region'
docker exec $_db_docker psql -U panorama -c 'create sequence panoramas_region_id_seq'
docker exec $_db_docker psql -U panorama -c "alter table panoramas_region alter id set default nextval('panoramas_region_id_seq')"
docker exec $_db_docker /bin/update-table.sh panorama panoramas_panorama public panorama
