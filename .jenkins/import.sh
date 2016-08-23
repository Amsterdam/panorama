#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill db-backup importer; dc rm -f db-backup importer' EXIT

dc kill render database; dc rm -f render database

echo "clean up old volumes";
docker volume ls -qf dangling=true | xargs -r docker volume rm;
echo "clean up volumes completed";

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc build
dc run --rm importer
dc run --rm db-backup
