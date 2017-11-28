#!/bin/bash

# use the packaged update scripts
#   in the background as to not to mess with the other entrypoint scripts

/bin/dl_and_import_for_swarm.sh &

echo STARTED DOWNLOAD AND IMPORT SCRIPT