#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

# wait for postgres
while ! nc -z database 5432
do
	echo "Waiting for PostgreSQL..."
	sleep 2
done
