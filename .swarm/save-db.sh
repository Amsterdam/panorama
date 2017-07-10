#!/usr/bin/env bash



docker exec -it {{database}} psql -U panorama -c 'create table region_export as select region_type, left_top_x, left_top_y, right_top_x, right_top_y, left_bottom_x, left_bottom_y, right_bottom_x, right_bottom_y, detected_by, pano_id from panoramas_region'
docker exec -it {{database}} pg_dump -Fc -t region_export* -d panorama -U panorama -f /tmp/20170516_regions.sql
docker cp {{database}}:/tmp/20170516_regions.sql /tmp/