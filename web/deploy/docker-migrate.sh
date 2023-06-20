#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

echo "Migrating db"
yes yes | python3 ./manage.py migrate --noinput
