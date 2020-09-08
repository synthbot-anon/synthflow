#!/bin/bash

cid="$(docker ps --filter name="synthflow" -q)"
docker exec -u celestia -it $cid /data/src/synthflow/scripts/run-airflow.sh
