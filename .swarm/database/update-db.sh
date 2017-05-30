#!/usr/bin/env bash
set -eu

cd /tmp
rm -f $1_latest.gz
wget -nc https://admin:tIixt7p4lsSBCrXNoXRq@admin.datapunt.amsterdam.nl/postgres/$1_latest.gz
dropdb --if-exists -U postgres $1 || echo "Could not drop $1, continuing"
createuser -U postgres $1 || echo "Could not create $1, continuing"
createuser -U postgres $1_read || echo "Could not create $1, continuing"
SECONDS=0
pg_restore --if-exists -j 1 -c -C -d postgres -U postgres /tmp/$1_latest.gz
echo "Finished pg_restore $1"
duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
rm -f $1_latest.gz
