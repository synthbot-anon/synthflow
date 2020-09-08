#!/bin/bash

source ~/.bashrc
rm /data/airflow/airflow-scheduler.pid || true
rm /data/airflow/airflow-webserver.pid || true
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
It looks like you're set up! Run utils/run-airflow.sh to start the scheduler
and webserver. You can connect to the webserver by navigating to:

  http://localhost:8881/

You can put your data in run-data/downloaded. After running the dags, upload
everything in run-data/generated to your Google Drive, make it public, and post the folder link in the thread.
HELP

