#!/bin/bash

export AIRFLOW_HOME=/data/airflow

airflow scheduler -D
airflow webserver
kill $(cat /data/airflow/airflow-scheduler.pid)
