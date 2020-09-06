import sys
sys.path.append('/data/src/')

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import tempfile
from glob import glob

from datapipes.loaders.tacotron_loader import TacotronLoader
from datapipes import phonemes
from datapipes import mfa
import subprocess
import os

# def create_g2p_model(input_phonedict, output_path):
#     with tempfile.TemporaryDirectory() as tmpdir:
#         if not os.path.isdir(input_phonedict):
#             # if it's a single dictionary file, use that directly
#             training_path = input_phonedict
#         else:
#             # if it's a directory, use all dictionaries in it
#             training_path = f'tmpdir/training_dict.txt'
#             dictionary = phonemes.PhoneticDictionary()
#             for filepath in glob(f'{input_phonedict}/*.txt'):
#                 dictionary.load_dictionary(filepath)
#             dictionary.pandas().to_csv(training_path, sep='\t', index=False, header=False)

#         subprocess.run(
#             [
#                 "/opt/mfa/bin/mfa_train_g2p",
#                 input_phonedict,
#                 output_path,
#             ],
#             cwd="/opt/mfa",
#         )

def create_g2p_model(input_phonedict, output_path):
    # load the training dictionary
    dictionary = phonemes.PhoneticDictionary()
    if not os.path.isdir(input_phonedict):
        dictionary.load_dictionary(input_phonedict)
    else:
        for filepath in glob(f'{input_phonedict}/*.txt'):
            dictionary.load_dictionary(filepath)

    # generate the g2p model
    generator = mfa.MfaDictionaryGenerator()
    generator.load_dictionary(dictionary.pandas())
    generator.dump_g2p_model(output_path)


def create_dags(name, prefix, suffix, input_path):
    dag = DAG(f'{prefix}g2p-model{suffix}',
              description=
              f'Create a grapheme-to-phoneme model for {name}',
              schedule_interval=None,
              start_date=days_ago(0),
              is_paused_upon_creation=False)

    g2p_path = f'/data/generated/{name}.g2p.zip'

    transcript_task = PythonOperator(
        task_id='create_g2p_model',
        python_callable=create_g2p_model,
        op_args=[input_path, g2p_path],
        dag=dag)



    return [dag]