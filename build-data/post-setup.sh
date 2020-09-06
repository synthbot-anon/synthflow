#!/bin/bash

service postgresql start
until pg_isready; do sleep 1; done

su postgres -c 'createuser -s celestia'
su celestia -c 'createdb airflow'

