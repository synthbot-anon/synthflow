#!/bin/bash

cid="$(docker ps --filter ancestor=synthflow:latest -q)"
docker exec -u celestia -it $cid /data/scripts/run-airflow.sh
