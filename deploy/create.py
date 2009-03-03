import os
import shutil

def create_update_archive(base, configfile, components="all"):
    if not os.path.isdir(base):
        os.makedirs(base)

    shutil.copy(configfile, os.path.join(base, 'deploy.cfg'))
    return base
