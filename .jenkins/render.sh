#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p panorama -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill render' EXIT

dc build
dc up -d database
sleep 20
dc scale render=1
sleep 45
dc scale render=2
sleep 60
dc scale render=3
sleep 75
dc scale render=4
sleep 90
dc scale render=5
sleep 105
dc scale render=6

docker wait panorama_render_1 panorama_render_2 panorama_render_3 panorama_render_4 panorama_render_5 panorama_render_6

dc stop database
