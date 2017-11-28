#!/usr/bin/env bash

set -eu
set -x

/bin/update-table.sh panorama panoramas_region public panorama
/bin/update-table.sh panorama panoramas_panorama public panorama