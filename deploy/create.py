from os import makedirs
from os.path import join, isdir
from shutil import copy

def create_update_archive(base, configfile, components="all"):
    for subdir in ['databases', 'code', 'files']:
        d = join(base, subdir)
        if not isdir(d):
            makedirs(d)

    copy(configfile, base)
    return base
