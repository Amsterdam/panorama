#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill render; dc rm -f render' EXIT

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

# keep the script alive while rendering - rendernodes quit when done
while (docker ps | grep render > /dev/null); do
	sleep 60
done

dc stop database
