#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p panorama -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill db-backup importer; dc rm -f db-backup importer' EXIT

dc kill render database; dc rm -f render database

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc build
dc run --rm importer
dc run --rm db-backup
