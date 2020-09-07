#!/bin/bash

(cd /tmp/; ./post-setup.sh)
(cd /tmp/spec; ./post-setup.sh)

sudo -i -u celestia bash --init-file /data/src/synthflow/scripts/celestia-on-start.sh
exit
