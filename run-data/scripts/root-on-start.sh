#!/bin/bash

service postgresql start
until pg_isready; do sleep 1; done

sudo -i -u celestia bash --init-file /data/scripts/celestia-on-start.sh
exit
