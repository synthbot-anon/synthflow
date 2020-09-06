import sys
sys.path.append('/data/src/')

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

from datapipes.loaders.tacotron_loader import TacotronLoader
from datapipes import mfa
from synthflow import air
import os
import pandas

# TODO: replace joblib Parallel() with dask delayed()
# TODO: replace SequentialExecutor with DaskExecutor

def load_transcripts(character, input_directory, output_parquet):
    loader = TacotronLoader()
    loader.load_directory(input_directory)
    result = loader.pandas()
    result['character'] = character
    result.to_parquet(output_parquet, engine='fastparquet', compression='UNCOMPRESSED')

def dump_mfa_corpus(input_parquet, output_directory, output_parquet):
    corpus = mfa.MfaCorpus()
    transcripts = pandas.read_parquet(input_parquet)
    corpus.load_transcribed_audio(transcripts)
    corpus.dump(output_directory)

def create_dictionary(mfa_corpus, g2p_model, output_path):
    generator = mfa.MfaDictionaryGenerator()
    generator.set_g2p_model(g2p_model)
    generator.set_mfa_corpus_dump(mfa_corpus)
    result_paths = generator.dump_g2p_dictionaries(output_path)



def create_dags(character, prefix, suffix, input_directory):
    dag = DAG(f'{prefix}full-preproc{suffix}',
              description=
              f'Expand and package the audio data for {character}',
              schedule_interval=None,
              start_date=days_ago(0),
              is_paused_upon_creation=False)

    transcripts_parquet = f'/data/generated/{character}.transcript.parquet'

    transcript_task = PythonOperator(
        task_id='load_transcripts',
        python_callable=load_transcripts,
        op_args=[character, input_directory, transcripts_parquet],
        dag=dag)

    mfa_corpus = f'/data/generated/{character}.mfa_corpus'
    mfa_corpus_task = PythonOperator(
        task_id='dump_mfa_corpus',
        python_callable=dump_mfa_corpus,
        op_args=[transcripts_parquet, mfa_corpus])
    transcript_task >> mfa_corpus_task

    dictionary_path = f'/data/uploadable/{character}.phonedict'
    os.makedirs(dictionary_path, exist_ok=True)
    for g2p_model in air.collect_files('*.g2p.zip'):
        dictionary_name = g2p_model[:-8]
        output_path = f'{dictionary_path}/{character}-{dictionary_name}.phonedict'
        dictionary_task = PythonOperator(
            task_id='character_dictionary',
            python_callable=create_dictionary,
            op_args=[mfa_corpus, g2p_model, output_path])

        mfa_corpus_task >> dictionary_task


    return [dag]


# separate task for each augmentation / transformation
# immutable input -> augmentation or transformation
# at the end: collate files with audiofn split by character
# ... collect all parquet files with an audio column, split files by character
# ... rename audio paths to match the upcoming archive file
# ... since audio refers to files, collect all relevant audio files into archives