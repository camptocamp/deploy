import os

def get_archive_dir(path):
    if not path.endswith('/'):
        path += '/'
    return os.path.dirname(path)

