#!/bin/bash

cid="$(docker ps --filter ancestor=synthflow:latest -q)"
docker exec -u celestia -it $cid /data/src/synthflow/scripts/run-airflow.sh
