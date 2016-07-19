#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc rm -f' EXIT

dc scale render=1
sleep 60
dc scale render=2
sleep 60
dc scale render=3
sleep 60
dc scale render=4
sleep 60