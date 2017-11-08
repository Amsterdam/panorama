#!/bin/bash

# use the packaged single-thread and single-transaction update script
#   in the background as to not to mess with entrypoint script

/bin/import-single.sh panorama root &

echo STARTED UPDATE SCRIPT