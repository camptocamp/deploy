from tarfile import is_tarfile
from os.path import join, isdir

def create_apache_config(dest, content):
    f = file(dest, 'w').write(content)

def get_project_config(name):
    if isdir(name):
        # FIXME: check if the file is readable
        return join(name, 'deploy.conf')
    else:
        raise NotImplementedError

def extract_project(name):
    pass
