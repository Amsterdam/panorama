#!/usr/bin/env bash

set -u
set -e

# wait for rabbit_mq
while ! nc -z queue 5672
do
	echo "Waiting for rabbit_mq..."
	sleep 2
done

# wait for postgres
while ! nc -z database 5432
do
	echo "Waiting for postgres..."
	sleep 2
done
