#!/usr/bin/python

from airflow import DAG
from airflow.utils.db import provide_session
from airflow.models import Variable
from importlib import import_module
import os
import sys
import re

sys.path.append('/data/src')
__dag_index = 0

for filename in os.listdir('/data/downloaded'):
    path = f'/data/downloaded/{filename}'
    parts = filename.split('.')
    name, loaders = parts[0], parts[1:]

    if not name:
        continue

    # normalize the name to something airflow likes
    name = re.sub(r'[^A-Za-z0-9\-._ ]', '', name)

    if len(loaders) != 1:
        # eventually, turn sequential loaders into recursive subdags
        continue

    try:
        module = import_module(f'synthflow.events.on_{loaders[0]}')
        print('loading', loaders[0])
        for dag in module.create_dags(name, '', f'.{name.replace(" ", "_")}', path):
            globals()[f'generated_dag{__dag_index}'] = dag
            __dag_index += 1
        print('done')
    except Exception as e:
        print(e)
