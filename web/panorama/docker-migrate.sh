#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

yes yes | python manage.py migrate --noinput

