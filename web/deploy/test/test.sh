#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

echo "Waiting for db"
source /deploy/docker-wait.sh
source /deploy/docker-migrate.sh

echo "Running unit tests"
./manage.py test
