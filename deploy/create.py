from os import makedirs
from os.path import join, isdir
from shutil import copy

def create_update_archive(base, configfile, components="all"):
    if not isdir(base):
        makedirs(base)

    copy(configfile, base)
    return base
