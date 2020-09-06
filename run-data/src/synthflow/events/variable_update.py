#!/usr/bin/python

from airflow.utils.db import provide_session
from airflow.models import Variable
from importlib import import_module
import sys

sys.path.append('/data/src')


dag_generators = {
    'tacotron': ...,
    'clipper': ...,
}

@provide_session
def calc_required_dags(session=None):
    result = set()

    # monitor download directory for changes
    # each known dataablob should have key=reference, value=details
    # based on details, append the required dag
    for var in session.query(Variable):
        location = var.key
        info = var.val
        relevant_dags = dag_generators(location, info)






try:
    mod = import_module('dags.dynamic.on_tacotron')
    print(mod.dag)

except:
    print('failed to load on_tacotron.py')
    raise
