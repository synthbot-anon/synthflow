from glob import glob

def collect_files(pattern):
    for file in glob(f'/data/downloaded/{pattern}'):
        yield file

    for file in glob(f'/data/generated/{pattern}'):
        yield file

    for file in glob(f'/data/uploadable/{pattern}'):
        yield file
