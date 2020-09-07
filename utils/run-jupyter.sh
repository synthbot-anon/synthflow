#!/bin/bash

specialization="$1"
cid="$(docker ps --filter name="synthflow-$specialization" -q)"
docker exec -u celestia -it $cid /data/src/synthflow/scripts/run-jupyter.sh
