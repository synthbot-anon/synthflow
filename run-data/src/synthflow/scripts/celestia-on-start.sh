#!/bin/bash

source ~/.bashrc
rm -f /data/airflow/airflow-scheduler.pid || true
rm -f /data/airflow/airflow-webserver.pid || true
airflow initdb
psql airflow -f /data/src/synthflow/scripts/db-triggers.psql
clear -x

echo -e "\e[1;31m"
cat<<TF
________              ___________ _______________                
__  ___/____  __________  /___  /____  ____/__  /________      __
_____ \__  / / /_  __ \  __/_  __ \_  /_   __  /_  __ \_ | /| / /
____/ /_  /_/ /_  / / / /_ _  / / /  __/   _  / / /_/ /_ |/ |/ / 
/____/ _\__, / /_/ /_/\__/ /_/ /_//_/      /_/  \____/____/|__/  
       /____/                                                    
TF


echo -e "\e[0;33m"
cat <<HELP
It looks like you're set up! I'll eventually add more information here explaining how to get started. For now, please go through the readme if you haven't already.
HELP

