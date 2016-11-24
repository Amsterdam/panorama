#!/bin/bash

# use the packaged updatescript in the background to not mess with entrypoint script
/bin/update-db.sh panorama &

echo STARTED UPDATE SCRIPT