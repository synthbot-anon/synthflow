#!/bin/bash

(cd /tmp/; ./pre-run.sh)
(cd /tmp/spec; ./pre-run.sh)

sudo -i -u celestia bash --init-file /data/src/synthflow/scripts/celestia-on-start.sh
exit
