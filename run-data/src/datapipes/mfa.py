from glob import glob
import io
from joblib import Parallel, delayed
import librosa
import os
import re
import shutil
import soundfile
import subprocess
import tempfile
import tqdm

import pandas
import praatio.tgio



def write_transcript_textgrid(transcript: str, duration: float,
                              output_path: str):
    normalized = re.sub(r'[.?!,;"]', ' ', transcript)
    normalized = normalized.replace('-', '').replace("'", '')

    textgrid = praatio.tgio.Textgrid()
    utterance = praatio.tgio.IntervalTier("utt", [], 0, duration)
    utterance.insertEntry(
        praatio.tgio.Interval(start=0, end=duration, label=normalized))
    textgrid.addTier(utterance)

    textgrid.save(output_path, useShortForm=False)


class MfaDictionaryGeneratorPaths:
    def __init__(self, path):

        self.generated_dictionary_dir = f"{path}/generated_dictionaries"
        os.makedirs(self.generated_dictionary_dir, exist_ok=True)


class MfaDictionaryGenerator:
    def __init__(self):
        self.dictionaries = []
        self.corpus = None
        self.g2p_model_path = None

    def load_dictionary(self, pandas):
        self.dictionaries.append(pandas)

    def set_g2p_model(self, path):
        self.g2p_model_path = path

    def set_mfa_corpus_dump(self, dump):
        self.corpus = dump

    def dump_g2p_dictionaries(self, path):
        os.makedirs(path, exist_ok=True)

        def generate_dictionary(row):
            character = row.character
            corpus_path = row.path
            dictionary_path = f"{path}/{character}.phonedict"

            subprocess.run(
                [
                    "/opt/mfa/bin/mfa_generate_dictionary",
                    self.g2p_model_path,
                    corpus_path,
                    dictionary_path,
                ],
                cwd="/opt/mfa",
            )

            return [dictionary_path, 'g2p_dictionary', character]

        result = Parallel(n_jobs=-1)(
            delayed(generate_dictionary)(row) for row in tqdm.tqdm(
                self.corpus.itertuples(), "Generating character dictionary"))

        return pandas.DataFrame(result,
                                columns=['path', 'contents', 'character'])

    def dump_g2p_model(self, output_path):
        with tempfile.NamedTemporaryFile() as train_dictionary_file:
            dictionary_data = pandas.concat(self.dictionaries)
            dictionary_data.to_csv(train_dictionary_file.name,
                                   sep='\t',
                                   index=False,
                                   header=False)

            subprocess.run(
                [
                    "/opt/mfa/bin/mfa_train_g2p",
                    train_dictionary_file.name,
                    output_path,
                ],
                cwd="/opt/mfa",
            )

        return pandas.DataFrame([{
            'path': output_path,
            'contents': 'g2p_model',
        }])


class MfaCorpus:
    def __init__(self):
        self.transcribed_audio = []

    def load_corpus(self, path):
        # TODO: figure out how to turn a dump into a parquet file
        # maybe use these common functions: dump(), archive(), pandas()
        # reload through load_archive
        # ... maybe generically replace dump() with archive() + ratarmount for read-only access



    def load_transcribed_audio(self, pandas):
        """ 

        The pandas frame must have the following columns:
            - audio_path
            - transcript
            - character
        """
        self.transcribed_audio.append(pandas)

    def dump(self, path):
        os.makedirs(path, exist_ok=True)
        transcript_data = pandas.concat(self.transcribed_audio)
        transcript_data = transcript_data[
            transcript_data['audio_path'].notna()]
        transcript_data = transcript_data[
            transcript_data['transcript'].notna()]

        total_count = transcript_data.shape[0]
        characters = set()

        for character in transcript_data["character"].unique():
            os.makedirs(f"{path}/{character}/", exist_ok=True)
            characters.add(character)

        def _dump_single(row):
            # MFA expects each character's corpus to be placed in a separate sub-directory
            # and the corpus to consisted of paired files file1.textgrid, file1.wav, ...
            # where the textgrid contains the transcript and the wav contains 16khz audio

            index = row.Index
            transcript = row.transcript
            character = row.character
            audio_path = row.audio_path

            if not transcript or not audio_path:
                return

            out_audio_path = f"{path}/{character}/{index}.wav"
            out_textgrid_path = f"{path}/{character}/{index}.textgrid"

            if os.path.exists(out_audio_path) and os.path.exists(
                    out_textgrid_path):
                return

            data, rate = librosa.load(audio_path, sr=16000)
            duration = len(data) / float(rate)

            # out_textgrid_path = f"{path}/{character}/{index}.textgrid"
            write_transcript_textgrid(transcript, duration, out_textgrid_path)

            # out_audio_path = f"{path}/{character}/{index}.wav"
            soundfile.write(out_audio_path, data, rate)

        Parallel(n_jobs=-1, prefer="threads")(
            delayed(_dump_single)(row)
            for row in tqdm.tqdm(transcript_data.itertuples(),
                                 total=total_count,
                                 desc="Creating MFA corpus"))

        def _gen():
            for character in characters:
                yield [f"{path}/{character}", "mfa_corpus", character]

        return pandas.DataFrame(_gen(),
                                columns=["path", "contents", "character"])


class AlignmentPaths:
    def __init__(self, path):
        self.dictionary = f'{path}/dictionary.txt'


class MfaAlignments:
    def __init__(self):
        self.corpus = []
        self.dictionaries = []
        self.alignments = []

    def load_mfa_dump(self, dump):
        self.corpus.append(dump)

    def load_dictionary(self, pandas):
        self.dictionaries.append(pandas)

    def load_alignment_dump(self, dump):
        self.alignments.append(dump)

        # read the results into a dataframe

        # without acoustic model (cd /opt/mfa/; /opt/mfa/bin/mfa_align -v /home/celestia/mfa_corpus/Adachi\ Tohru/ /home/celestia/align-tmp/dictionary.txt  /home/celestia/char_dictionaries/generated_model.zip /home/celestia/mfa_alignments/adachi/)
        # with acoustic model (cd /opt/mfa/; /opt/mfa/bin/mfa_train_and_align -v /home/celestia/mfa_corpus/Adachi\ Tohru/ /home/celestia/align-tmp/dictionary.txt /home/celestia/mfa_alignments/adachi)
        # todo: have mfa output the model to a target directory

    def dump(self,
             path,
             acoustic_model='/opt/mfa/pretrained_models/english.zip'):
        print('dumping alignments')
        # open a temp directory
        # need utility class for dealing with temp directories

        # create dictionary path
        dictionary_path = ''  #...
        dictionary_data = pandas.concat(self.dictionaries)
        dictionary_data.to_csv(dictionary_path,
                               sep='\t',
                               index=False,
                               header=False)

        corpus = pandas.concat(self.corpus)

        def _dump_single(character, corpus, mfa_cache_path):
            mfa_cache_path = ''  # ...
            if corpus.shape[0] == 1:
                corpus_path = corpus.path
            else:
                print(
                    'warning: case where a corpus is split across directories is not yet supported'
                )
                # paths.corpus = '/home/celestia/align-tmp/adachi'
                # copy data into corpus_path
                return

            if acoustic_model:
                subprocess.run([
                    '/opt/mfa/bin/mfa_align', '-v', '-t', mfa_cache_path,
                    corpus_path, dictionary_path, acoustic_model,
                    f'{path}/{character}'
                ])
            else:
                subprocess.run([
                    '/opt/mfa/bin/mfa_train_and_align', '-v', '-t', tmpdir,
                    corpus_path, dictionary_path, f'{path}/{character}'
                ])

        Parallel(n_jobs=-1, prefer='threads')(
            delayed(_dump_single)(character, corpus)
            for character, corpus in tqdm(corpus.groupby(by=['character'])))

        # return new dumps + self.alignments, remove duplicates

    def pandas(self):
        # flow: load_mfa_dump(); load_dictionary(); dump(); load_alignment_dump(); pandas()
        pass

    def debugger(self):
        pass


class MfaDebugger:
    def __init__(self):
        pass

    def run_tests(self):
        pass


# character MFA has trouble with
# word = word.replace('-', '').replace("'", '')
# pronunciation = pronunciation.replace('-', '').replace("'", '')
